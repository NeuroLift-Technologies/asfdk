"""OTOI policy gateway for ACDT, DPoP, CSG, and reconciliation."""
from __future__ import annotations

import time
import uuid
from collections.abc import Mapping
from typing import Any, Callable, Dict, List, Optional, Set

from .crypto import (
    b64url,
    canonical_json,
    decode_dpop,
    jwk_thumbprint,
    load_and_verify_charter,
    sha256,
    verify_charter,
    verify_dpop_signature,
)
from .errors import PolicyDenied
from .models import (
    ACDT,
    Consent,
    CrisisLevel,
    DispatchResult,
    OperationDefinition,
    OutboundRequest,
    RuntimeConfig,
    TerminalState,
)
from .provenance import CompositeSynthesisGate, IngressClassifier
from .retention import AuditLedger
from .rrta import SafeResponseHandler
from .store import (
    MemoryReservationStore,
    SQLiteReservationStore,
    request_hash,
    validate_reservation,
)


class PolicyGateway:
    """Fail-closed enforcement boundary; never holds a lock across adapter I/O."""

    def __init__(self, config: RuntimeConfig) -> None:
        self.config = config
        principal = load_and_verify_charter(config.charter_path, config.trusted_charter_keys)
        self.agent_id = principal["agent_id"]
        self.receiver_capabilities = principal["capabilities"]
        storage_path = None if config.consent == Consent.NONE else (
            config.storage_path or ".asfdk/adr001.sqlite3"
        )
        self.ledger = AuditLedger(
            config.consent, storage_path=storage_path,
            local_single_user=config.local_single_user,
            encryption_key=config.audit_encryption_key,
        )
        if config.consent == Consent.NONE:
            self.store = MemoryReservationStore()
        else:
            self.store = SQLiteReservationStore(
                storage_path, response_cipher=self.ledger.cipher,
                retain_responses=config.consent in (Consent.ACTIVE, Consent.EXPLICIT),
            )
        self.ingress = IngressClassifier()
        self.csg = CompositeSynthesisGate(self.ingress)
        self.safe_responses = SafeResponseHandler()
        self.crisis_level = CrisisLevel.GREEN
        self._tokens: Dict[str, ACDT] = {}
        self._revoked_sessions: Set[str] = set()
        self._revoked_tokens: Set[str] = set()
        self._kill_switch = False
        self._operations: Dict[str, OperationDefinition] = {}

    def register_operation(self, definition: OperationDefinition) -> None:
        """Register a trusted adapter operation definition."""
        if not definition.name:
            raise PolicyDenied("INVALID_OPERATION", "Operation name is required")
        self._operations[definition.name] = definition

    def _validate_operation(self, request: OutboundRequest) -> None:
        """Validate the request against its trusted operation definition."""
        if not request.operation:
            raise PolicyDenied(
                "UNKNOWN_OPERATION", "A registered operation name is required",
            )
        definition = self._operations.get(request.operation)
        if definition is None:
            raise PolicyDenied("UNKNOWN_OPERATION", f"Operation '{request.operation}' is not registered")
        if (request.method.upper() != definition.method.upper()
                or request.url != definition.url
                or request.audience != definition.audience
                or request.destination != definition.destination
                or request.required_capability != definition.required_capability
                or request.boundary != definition.boundary):
            raise PolicyDenied(
                "OPERATION_MISMATCH",
                "Request metadata does not match the registered operation definition",
            )

    def synthesize(self, payload: Any, provenance: Any) -> Any:
        """Attest a derived payload and its complete contributor lineage."""
        return self.ingress.derive(payload, provenance)

    def mint_root(self, dpop_jkt: str, *, now: Optional[float] = None) -> ACDT:
        if not self.config.root_audience or not self.config.human_task_capabilities:
            raise PolicyDenied("INVALID_RUNTIME_CONFIG", "Root audience and human-task grants are required")
        return self._mint(
            subject=self.agent_id, audience=self.config.root_audience,
            human_task=self.config.human_task_capabilities,
            parent=None, receiver=self.receiver_capabilities,
            rem_depth=self.config.root_depth, dpop_jkt=dpop_jkt,
            session_id=self.config.root_session_id, now=now,
        )

    def delegate(self, parent: ACDT, *, subject: str, audience: str,
                 human_task_capabilities: frozenset, receiver_capabilities: Optional[frozenset] = None,
                 dpop_jkt: str, receiver_charter: Optional[Mapping[str, Any]] = None,
                 user_decides: Optional[Callable[[Dict[str, Any]], bool]] = None) -> ACDT:
        self._verify_token(parent, expected_audience=None)
        if parent.rem_depth < 1:
            raise PolicyDenied("DELEGATION_DEPTH_EXHAUSTED", "No delegation depth remains")
        if receiver_charter is not None:
            verified = verify_charter(receiver_charter, self.config.trusted_charter_keys)
            if verified["agent_id"] != subject:
                raise PolicyDenied("DENY_UNVERIFIED_PRINCIPAL", "Receiver identity does not match charter")
            receiver = verified["capabilities"]
        else:
            decision = {"subject": subject, "audience": audience, "parent_handoff_id": parent.handoff_id}
            if user_decides is None or user_decides(decision) is not True:
                raise PolicyDenied("USER_DECIDES", "Ephemeral sub-agent grant requires explicit approval")
            receiver = receiver_capabilities or frozenset()
        return self._mint(
            subject=subject, audience=audience, human_task=human_task_capabilities,
            parent=parent, receiver=receiver, rem_depth=parent.rem_depth - 1,
            dpop_jkt=dpop_jkt, session_id=parent.session_id,
        )

    def _mint(self, *, subject: str, audience: str, human_task: frozenset,
              parent: Optional[ACDT], receiver: frozenset, rem_depth: int,
              dpop_jkt: str, session_id: str, now: Optional[float] = None) -> ACDT:
        if not audience or not dpop_jkt or rem_depth < 0:
            raise PolicyDenied("INVALID_ACDT", "Audience, key binding, and non-negative depth are required")
        parent_grants = parent.capabilities if parent else receiver
        effective = frozenset(human_task) & parent_grants & receiver & self.config.sleepwalker_capabilities
        timestamp = time.time() if now is None else now
        handoff_id = str(uuid.uuid4())
        lineage = sha256(canonical_json({
            "parent": parent.lineage_hash if parent else None, "handoff_id": handoff_id,
            "subject": subject, "audience": audience,
        }))
        token = ACDT(
            token_id=str(uuid.uuid4()), subject=subject, audience=audience,
            capabilities=effective, rem_depth=rem_depth,
            # Child expiry is bounded by the parent's expiration.
            exp=min(timestamp + 300, parent.exp) if parent else timestamp + 300,
            cnf_jkt=dpop_jkt, session_id=session_id, handoff_id=handoff_id,
            lineage_hash=lineage, parent_token_id=parent.token_id if parent else None,
        )
        self._tokens[token.token_id] = token
        self.ledger.record("acdt_minted", {
            "handoff_id": handoff_id, "lineage_hash": lineage, "audience": audience,
        }, user_id=subject)
        return token

    def _verify_token(self, token: ACDT, *, expected_audience: Optional[str],
                      proof: Optional[str] = None, method: str = "", url: str = "") -> ACDT:
        current = self._tokens.get(token.token_id)
        if current != token or token.exp <= time.time():
            raise PolicyDenied("INVALID_ACDT", "ACDT is unknown or expired")
        if expected_audience is not None and token.audience != expected_audience:
            raise PolicyDenied("AUDIENCE_MISMATCH", "ACDT audience does not match the adapter")
        if proof is None:
            return token
        header, payload, signature, signing_input = decode_dpop(proof)
        verify_dpop_signature(header, signing_input, signature)
        try:
            if jwk_thumbprint(header["jwk"]) != token.cnf_jkt:
                raise PolicyDenied("DPOP_KEY_MISMATCH", "DPoP key is not bound to the ACDT")
            expected_htu = url.split("?", 1)[0].split("#", 1)[0]
            if payload["htu"] != expected_htu or payload["htm"] != method.upper():
                raise PolicyDenied("DPOP_INVALID", "DPoP method or URI mismatch")
            import hashlib
            expected_ath = b64url(hashlib.sha256(token.token_id.encode("ascii")).digest())
            if payload["ath"] != expected_ath:
                raise PolicyDenied("DPOP_INVALID", "DPoP access-token hash mismatch")
            now = time.time()
            iat = payload["iat"]
            if not isinstance(iat, int) or iat > now + 30 or iat < now - 300:
                raise PolicyDenied("DPOP_EXPIRED", "DPoP proof is outside its short lifetime")
            jti = payload["jti"]
            if not isinstance(jti, str) or not jti:
                raise PolicyDenied("DPOP_INVALID", "DPoP jti is required")
        except KeyError as err:
            raise PolicyDenied("DPOP_INVALID", "DPoP claim is missing") from err
        if not self.store.reserve_jti(token.cnf_jkt, jti, time.time() + 300):
            raise PolicyDenied("REPLAY_REJECTED", "DPoP proof was already used")
        return token

    def _assert_active(self, token: ACDT) -> None:
        if self._kill_switch or self.crisis_level in (CrisisLevel.RED, CrisisLevel.BLACK):
            raise PolicyDenied("CRISIS_REVOKED", "Crisis or kill-switch revocation is active")
        if token.session_id in self._revoked_sessions or token.token_id in self._revoked_tokens:
            raise PolicyDenied("SESSION_REVOKED", "Session or ACDT is revoked")

    def revoke(self, *, session_id: Optional[str] = None, token_id: Optional[str] = None,
               level: CrisisLevel = CrisisLevel.RED, kill_switch: bool = False) -> None:
        if level not in (CrisisLevel.RED, CrisisLevel.BLACK) and not kill_switch:
            raise PolicyDenied("INVALID_REVOCATION", "Revocation requires RED, BLACK, or kill-switch")
        self.crisis_level = level
        self._kill_switch = self._kill_switch or kill_switch
        if session_id:
            self._revoked_sessions.add(session_id)
            # Invalidate every grant already issued for the affected session,
            # including delegated children; recovery does not resurrect them.
            for tid, token in self._tokens.items():
                if token.session_id == session_id:
                    self._revoked_tokens.add(tid)
        if token_id:
            self._revoked_tokens.add(token_id)

    def recover(self, level: CrisisLevel) -> None:
        if level not in (CrisisLevel.GREEN, CrisisLevel.YELLOW):
            raise PolicyDenied("INVALID_RECOVERY", "Recovery requires GREEN or YELLOW")
        self.crisis_level = level
        self._kill_switch = False
        # Previously revoked sessions and tokens stay revoked until expiry;
        # fresh authorized grants can be minted after recovery.

    def update_consent(self, consent: Consent) -> None:
        if self.config.consent == Consent.NONE and consent != Consent.NONE:
            raise PolicyDenied(
                "CONSENT_REINITIALIZATION_REQUIRED",
                "Reinitialize to select a persistent reservation store",
            )
        self.ledger.update_consent(consent)
        if isinstance(self.store, SQLiteReservationStore):
            self.store.update_consent(consent, self.ledger.cipher)
        if consent == Consent.NONE:
            # Atomically transfer in-flight reservations and replay state to a
            # volatile memory store, then purge all durable rows and jti entries.
            old_store = self.store
            if isinstance(old_store, SQLiteReservationStore):
                rows = old_store.export_rows()
                jti = old_store.export_jti()
                old_store.clear()
                new_store = MemoryReservationStore()
                new_store.import_rows(rows)
                new_store.import_jti(jti)
                self.store = new_store
            else:
                self.store.clear()
                self.store = MemoryReservationStore()
        self.config.consent = consent

    def _safe_result(self, state: TerminalState = TerminalState.CANCELLED,
                     deferred: bool = False) -> DispatchResult:
        return DispatchResult(state=state, deferred=deferred,
                              safe_response=self.safe_responses.response())

    def _revoked_result(self, state: TerminalState = TerminalState.CANCELLED,
                        deferred: bool = False) -> DispatchResult:
        if self.crisis_level in (CrisisLevel.RED, CrisisLevel.BLACK) or self._kill_switch:
            return self._safe_result(state, deferred)
        return DispatchResult(state=state, deferred=deferred)

    async def dispatch(self, token: ACDT, request: OutboundRequest, dpop_proof: str) -> DispatchResult:
        # Holder proof is mandatory at the public dispatch boundary.
        if not dpop_proof or not isinstance(dpop_proof, str):
            raise PolicyDenied("PROOF_REQUIRED", "A valid DPoP proof is required")
        # Credential/revocation -> operation -> CSG -> scope precedence chain.
        self._verify_token(
            token, expected_audience=request.audience, proof=dpop_proof,
            method=request.method, url=request.url,
        )
        try:
            self._assert_active(token)
        except PolicyDenied as err:
            if err.code == "CRISIS_REVOKED":
                return self._safe_result()
            raise
        # Validate the actual request against its trusted operation definition.
        self._validate_operation(request)
        self.csg.authorize(
            request.destination, request.payload, request.provenance, request.synthesis,
        )
        if request.required_capability and request.required_capability not in token.capabilities:
            raise PolicyDenied("DENY_CAPABILITY", "Required capability is outside G_eff")
        is_write = self._is_write(request)
        if is_write and not request.idempotency_key:
            raise PolicyDenied("IDEMPOTENCY_KEY_REQUIRED", "Outbound writes require an idempotency key")

        self.ledger.record("egress_authorized", {
            "handoff_id": token.handoff_id, "lineage_hash": token.lineage_hash,
            "boundary": request.boundary, "destination": request.destination,
        }, user_id=token.subject)
        if not is_write:
            try:
                response = await self._dispatch_with_cancellation(token, request, None)
            except Exception:  # noqa: BLE001 - failed reads reconcile as UNKNOWN
                state, response = await self._reconcile_failure(request)
                return DispatchResult(state=state, response=response)
            if response is _CANCELLED or self._is_revoked(token):
                return self._revoked_result()
            return DispatchResult(state=TerminalState.COMMITTED, response=response)

        digest = request_hash({
            "payload": request.payload, "method": request.method, "url": request.url,
            "audience": request.audience, "destination": request.destination,
        })
        reservation = self.store.reserve(request.idempotency_key, token.session_id, digest, token.exp)
        validate_reservation(reservation, token.session_id, digest)
        if not reservation.created:
            if reservation.state == "RESERVED":
                raise PolicyDenied("REQUEST_IN_PROGRESS", "An identical write is already in flight")
            state = TerminalState(reservation.state)
            if reservation.deferred:
                return DispatchResult(state=state, deferred=True,
                                      safe_response=self.safe_responses.response()
                                      if self.crisis_level in (CrisisLevel.RED, CrisisLevel.BLACK) else None)
            return DispatchResult(state=state, response=reservation.response, cached=True,
                                  safe_response=self.safe_responses.response()
                                  if self.crisis_level in (CrisisLevel.RED, CrisisLevel.BLACK) else None)

        if self._is_revoked(token):
            self.store.finalize(reservation.key, TerminalState.CANCELLED)
            return self._revoked_result()
        try:
            response = await self._dispatch_with_cancellation(token, request, reservation.key)
            if response is _CANCELLED:
                return self._revoked_result()
        except Exception:  # noqa: BLE001 - adapter failure requires reconciliation
            state, response = await self._reconcile_failure(request)
            deferred = state == TerminalState.COMMITTED and self._is_revoked(token)
            self.store.finalize(reservation.key, state, response, deferred)
            if self.crisis_level in (CrisisLevel.RED, CrisisLevel.BLACK):
                return DispatchResult(state=state, deferred=deferred,
                                      safe_response=self.safe_responses.response())
            return DispatchResult(state=state, response=response, deferred=deferred)

        if self._is_revoked(token):
            self.store.finalize(reservation.key, TerminalState.COMMITTED, response, deferred=True)
            return self._revoked_result(TerminalState.COMMITTED, deferred=True)
        self.store.finalize(reservation.key, TerminalState.COMMITTED, response)
        return DispatchResult(state=TerminalState.COMMITTED, response=response)

    def _is_write(self, request: OutboundRequest) -> bool:
        # The trusted operation definition is authoritative for write classification;
        # a caller's write=False label cannot downgrade a registered write.
        if request.operation:
            definition = self._operations.get(request.operation)
            if definition and definition.is_write:
                return True
        if hasattr(request.adapter, "is_write"):
            trusted_write = request.adapter.is_write(request)
            if not isinstance(trusted_write, bool):
                raise PolicyDenied("INVALID_ADAPTER_CONTRACT", "is_write must return bool")
        else:
            trusted_write = request.method.upper() not in {"GET", "HEAD", "OPTIONS"}
        return request.write or trusted_write

    def _is_revoked(self, token: ACDT) -> bool:
        return (self._kill_switch or self.crisis_level in (CrisisLevel.RED, CrisisLevel.BLACK)
                or token.session_id in self._revoked_sessions or token.token_id in self._revoked_tokens)

    async def _dispatch_with_cancellation(self, token: ACDT, request: OutboundRequest,
                                          reservation_key: Optional[str]) -> Any:
        import asyncio
        task = asyncio.create_task(request.adapter.dispatch(request))
        cancellation_attempted = False
        while not task.done():
            if self._is_revoked(token) and hasattr(request.adapter, "cancel") and not cancellation_attempted:
                cancellation_attempted = True
                confirmed = await request.adapter.cancel(request)
                if confirmed:
                    task.cancel()
                    await asyncio.gather(task, return_exceptions=True)
                    if reservation_key is not None:
                        self.store.finalize(reservation_key, TerminalState.CANCELLED)
                    return _CANCELLED
            await asyncio.wait((task,), timeout=0.02)
        return await task

    async def _reconcile_failure(self, request: OutboundRequest) -> tuple[TerminalState, Any]:
        if hasattr(request.adapter, "status"):
            try:
                state = await request.adapter.status(request)
                if state in (TerminalState.COMMITTED, TerminalState.CANCELLED, TerminalState.UNKNOWN):
                    return state, None
            except Exception:  # noqa: BLE001 - status failure is explicitly UNKNOWN
                return TerminalState.UNKNOWN, None
        return TerminalState.UNKNOWN, None

    def resolve_unknown(self, idempotency_key: str, state: TerminalState,
                         response: Any = None) -> None:
        """Resolve an UNKNOWN reservation with later provider evidence."""
        if state not in (TerminalState.COMMITTED, TerminalState.CANCELLED):
            raise PolicyDenied(
                "INVALID_RESOLUTION", "Resolution requires COMMITTED or CANCELLED",
            )
        self.store.finalize(idempotency_key, state, response)

    def drain_deferred(self) -> List[DispatchResult]:
        if self.crisis_level not in (CrisisLevel.GREEN, CrisisLevel.YELLOW):
            return []
        rows = self.store.deferred()
        self.store.mark_surfaced([row.key for row in rows])
        return [DispatchResult(state=TerminalState.COMMITTED, response=row.response,
                               cached=True) for row in rows]


_CANCELLED = object()


__all__ = ["PolicyGateway"]
