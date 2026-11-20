"""AT-001 and fail-closed tests for the ADR-001 Python runtime slice."""
from __future__ import annotations

import asyncio
import json
import sqlite3
from dataclasses import replace

import pytest
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import ec, ed25519

from asfdk import (
    Consent,
    CrisisLevel,
    FoundationConfig,
    FoundationMode,
    OutboundRequest,
    PolicyDenied,
    PolicyGateway,
    RuntimeConfig,
    TerminalState,
    create_foundation,
    dpop_proof,
    jwk_thumbprint,
    public_jwk,
)
from asfdk.runtime import AuditLedger
from asfdk.runtime.crypto import b64url, canonical_json
from asfdk.runtime.store import MemoryReservationStore

ALL = frozenset({"calendar:read", "notes:read", "calendar:write", "private:respond"})


def make_charter(tmp_path, agent_id="root-agent", capabilities=ALL, tamper=False):
    private = ed25519.Ed25519PrivateKey.generate()
    jwk = public_jwk(private.public_key())
    manifest = {"agent_id": agent_id, "capabilities": sorted(capabilities), "public_key": jwk}
    manifest["signature"] = b64url(private.sign(canonical_json(manifest)))
    if tamper:
        manifest["capabilities"] = ["admin:*"]
    path = tmp_path / f"{agent_id}.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return str(path), {agent_id: jwk_thumbprint(jwk)}


def make_gateway(tmp_path, **overrides):
    charter_path, trusted = make_charter(tmp_path)
    values = {
        "charter_path": charter_path, "trusted_charter_keys": trusted,
        "sleepwalker_capabilities": ALL, "human_task_capabilities": ALL,
        "root_audience": "test://adapter", "root_depth": 2, "root_session_id": "session-at001",
    }
    values.update(overrides)
    gateway = PolicyGateway(RuntimeConfig(**values))
    key = ec.generate_private_key(ec.SECP256R1())
    token = gateway.mint_root(jwk_thumbprint(public_jwk(key.public_key())))
    return gateway, key, token


class RecordingAdapter:
    def __init__(self, response=None, handler=None):
        self.calls = []
        self.response = {"ok": True} if response is None else response
        self.handler = handler

    def is_write(self, request):
        return request.destination == "calendar:shared"

    async def dispatch(self, request):
        self.calls.append(request)
        if self.handler:
            return await self.handler(request)
        return self.response


def request(adapter, *, destination="user:private_response", provenance=(),
            capability="private:respond", write=False, key=None, payload=None):
    return OutboundRequest(
        adapter=adapter, method="POST", url="test://adapter/action?ignored=yes",
        audience="test://adapter", destination=destination,
        payload={"value": "calendar + note"} if payload is None else payload,
        provenance=tuple(provenance), required_capability=capability,
        write=write, idempotency_key=key,
    )


async def send(gateway, key, token, outbound, *, jti=None):
    provenance = outbound.provenance
    if not provenance:
        _, public = gateway.ingress.classify(
            outbound.payload, source_id="test-request", classification="public_external",
        )
        provenance = (public,)
    synthesis = outbound.synthesis or gateway.synthesize(outbound.payload, provenance)
    outbound = replace(outbound, provenance=provenance, synthesis=synthesis)
    return await gateway.dispatch(
        token, outbound,
        dpop_proof(key, outbound.method, outbound.url, token.token_id, jti=jti),
    )


def deny(code, function, *args, **kwargs):
    with pytest.raises(PolicyDenied) as caught:
        function(*args, **kwargs)
    assert caught.value.code == code
    return caught.value


@pytest.mark.asyncio
async def test_at001a_single_agent_private_response_and_shared_write_boundary(tmp_path):
    gateway, key, token = make_gateway(tmp_path)
    calendar_adapter = RecordingAdapter({"event": "Planning at 10"})
    note_adapter = RecordingAdapter({"note": "Private health note"})
    calendar_result = await send(gateway, key, token, request(
        calendar_adapter, destination="agent:private_context", capability="calendar:read",
    ))
    note_result = await send(gateway, key, token, request(
        note_adapter, destination="agent:private_context", capability="notes:read",
    ))
    _, calendar_prov = gateway.ingress.classify(
        calendar_result.response, source_id="calendar", classification="public_external",
    )
    _, note_prov = gateway.ingress.classify(
        note_result.response, source_id="private-note", classification="private",
    )
    provenance = (calendar_prov, note_prov)

    private_adapter = RecordingAdapter()
    private = await send(gateway, key, token, request(private_adapter, provenance=provenance))
    assert private.state == TerminalState.COMMITTED
    assert len(private_adapter.calls) == 1

    shared_adapter = RecordingAdapter()
    with pytest.raises(PolicyDenied) as caught:
        await send(gateway, key, token, request(
            shared_adapter, destination="calendar:shared", provenance=provenance,
            capability="calendar:write", write=True, key="at001a-shared",
        ))
    assert caught.value.code == "DENY_COMPOSITE_EGRESS"
    assert shared_adapter.calls == []


@pytest.mark.asyncio
async def test_at001b_multi_agent_split_read_and_orchestrator_synthesis(tmp_path):
    gateway, root_key, root = make_gateway(tmp_path)
    calendar_key = ec.generate_private_key(ec.SECP256R1())
    note_key = ec.generate_private_key(ec.SECP256R1())
    calendar_token = gateway.delegate(
        root, subject="calendar-agent", audience="test://adapter",
        human_task_capabilities=frozenset({"calendar:read"}),
        receiver_capabilities=frozenset(ALL), dpop_jkt=jwk_thumbprint(public_jwk(calendar_key.public_key())),
        user_decides=lambda decision: True,
    )
    note_token = gateway.delegate(
        root, subject="note-agent", audience="test://adapter",
        human_task_capabilities=frozenset({"notes:read"}),
        receiver_capabilities=frozenset(ALL), dpop_jkt=jwk_thumbprint(public_jwk(note_key.public_key())),
        user_decides=lambda decision: True,
    )
    assert calendar_token.capabilities == {"calendar:read"}
    assert note_token.capabilities == {"notes:read"}
    assert calendar_token.rem_depth == root.rem_depth - 1
    assert calendar_token.lineage_hash != note_token.lineage_hash

    cal_adapter = RecordingAdapter({"event": "Planning"})
    note_adapter = RecordingAdapter({"note": "Private"})
    cal = await send(gateway, calendar_key, calendar_token, request(
        cal_adapter, destination="agent:private_context", capability="calendar:read",
    ))
    note = await send(gateway, note_key, note_token, request(
        note_adapter, destination="agent:private_context", capability="notes:read",
    ))
    _, cal_prov = gateway.ingress.classify(cal.response, source_id="cal", classification="public_external")
    _, note_prov = gateway.ingress.classify(note.response, source_id="note", classification="private")

    private_adapter = RecordingAdapter()
    allowed = await send(gateway, root_key, root, request(
        private_adapter, provenance=(cal_prov, note_prov),
    ))
    assert allowed.state == TerminalState.COMMITTED
    denied_adapter = RecordingAdapter()
    with pytest.raises(PolicyDenied) as caught:
        await send(gateway, root_key, root, request(
            denied_adapter, destination="calendar:shared", provenance=(cal_prov, note_prov),
            capability="calendar:write", write=True, key="at001b-shared",
        ))
    assert caught.value.code == "DENY_COMPOSITE_EGRESS"
    assert denied_adapter.calls == []


def test_startup_rejects_tampered_or_unpinned_charter(tmp_path):
    path, trusted = make_charter(tmp_path, tamper=True)
    deny("DENY_UNVERIFIED_PRINCIPAL", PolicyGateway, RuntimeConfig(
        charter_path=path, trusted_charter_keys=trusted, sleepwalker_capabilities=ALL,
    ))
    path, _ = make_charter(tmp_path, agent_id="other")
    deny("DENY_UNVERIFIED_PRINCIPAL", PolicyGateway, RuntimeConfig(
        charter_path=path, trusted_charter_keys={}, sleepwalker_capabilities=ALL,
    ))


@pytest.mark.asyncio
async def test_create_foundation_verifies_charter_before_exposing_runtime(tmp_path):
    path, trusted = make_charter(tmp_path)
    foundation = await create_foundation(FoundationConfig(
        user_id="adr-user", mode=FoundationMode.FRAMEWORK_ONLY,
        runtime=RuntimeConfig(charter_path=path, trusted_charter_keys=trusted,
                              sleepwalker_capabilities=ALL),
    ))
    assert isinstance(foundation.runtime, PolicyGateway)
    await foundation.shutdown()
    with pytest.raises(RuntimeError):
        _ = foundation.runtime


def test_ephemeral_delegate_requires_user_decision_and_cannot_escalate(tmp_path):
    gateway, _key, root = make_gateway(tmp_path, root_depth=1)
    deny("USER_DECIDES", gateway.delegate, root, subject="sub", audience="test://adapter",
         human_task_capabilities=ALL, receiver_capabilities=ALL, dpop_jkt="key")
    child = gateway.delegate(
        root, subject="sub", audience="test://adapter", human_task_capabilities=ALL,
        receiver_capabilities=ALL, dpop_jkt="key", user_decides=lambda _: True,
    )
    assert child.rem_depth == 0
    deny("DELEGATION_DEPTH_EXHAUSTED", gateway.delegate, child, subject="grandchild",
         audience="test://adapter", human_task_capabilities=ALL,
         receiver_capabilities=ALL, dpop_jkt="key", user_decides=lambda _: True)


def test_ingress_default_taint_and_invalid_classification(tmp_path):
    gateway, _, _ = make_gateway(tmp_path)
    _, provenance = gateway.ingress.classify({"raw": True}, source_id="unlabeled")
    assert provenance.classification == "unknown_taint"
    assert provenance.no_derived_egress is True
    deny("DENY_UNCLASSIFIED_INGRESS", gateway.ingress.classify, {}, source_id="bad",
         classification="trusted_by_assertion")
    forged = replace(provenance, classification="public_external", no_derived_egress=False)
    deny("DENY_COMPOSITE_EGRESS", gateway.csg.authorize, "calendar:shared", None, (forged,))


@pytest.mark.asyncio
async def test_dpop_replay_and_audience_rejected_before_adapter(tmp_path):
    gateway, key, token = make_gateway(tmp_path)
    adapter = RecordingAdapter()
    outbound = request(adapter)
    _, public = gateway.ingress.classify(
        outbound.payload, source_id="proof-request", classification="public_external",
    )
    outbound = replace(
        outbound, provenance=(public,), synthesis=gateway.synthesize(outbound.payload, (public,)),
    )
    proof = dpop_proof(key, outbound.method, outbound.url, token.token_id, jti="once")
    first = await gateway.dispatch(token, outbound, proof)
    assert first.state == TerminalState.COMMITTED
    with pytest.raises(PolicyDenied) as caught:
        await gateway.dispatch(token, outbound, proof)
    assert caught.value.code == "REPLAY_REJECTED"
    assert len(adapter.calls) == 1

    wrong = request(adapter)
    wrong = OutboundRequest(**{**wrong.__dict__, "audience": "test://wrong"})
    with pytest.raises(PolicyDenied) as caught:
        await send(gateway, key, token, wrong)
    assert caught.value.code == "AUDIENCE_MISMATCH"
    assert len(adapter.calls) == 1


@pytest.mark.asyncio
async def test_idempotent_retry_returns_cache_without_second_adapter_write(tmp_path):
    gateway, key, token = make_gateway(tmp_path)
    adapter = RecordingAdapter({"commit_id": "commit-1"})
    outbound = request(adapter, destination="calendar:shared", capability="calendar:write",
                       write=True, key="write-1")
    first = await send(gateway, key, token, outbound)
    second = await send(gateway, key, token, outbound)
    assert first.cached is False
    assert second.cached is True
    assert second.response == {"commit_id": "commit-1"}
    assert len(adapter.calls) == 1
    changed = request(adapter, destination="calendar:shared", capability="calendar:write",
                      write=True, key="write-1", payload={"different": True})
    with pytest.raises(PolicyDenied) as caught:
        await send(gateway, key, token, changed)
    assert caught.value.code == "IDEMPOTENCY_CONFLICT"
    assert len(adapter.calls) == 1


@pytest.mark.asyncio
async def test_csg_precedes_scope_denial_and_adapter_never_receives_payload(tmp_path):
    gateway, key, token = make_gateway(tmp_path, human_task_capabilities=frozenset({"notes:read"}))
    adapter = RecordingAdapter()
    _, restricted = gateway.ingress.classify("secret", source_id="note", classification="private")
    with pytest.raises(PolicyDenied) as caught:
        await send(gateway, key, token, request(
            adapter, destination="calendar:shared", provenance=(restricted,),
            capability="not:granted", write=True, key="precedence",
        ))
    assert caught.value.code == "DENY_COMPOSITE_EGRESS"
    assert adapter.calls == []


@pytest.mark.asyncio
async def test_red_revocation_is_zero_disclosure_and_blocks_dispatch(tmp_path):
    gateway, key, token = make_gateway(tmp_path)
    gateway.revoke(session_id=token.session_id, level=CrisisLevel.RED)
    adapter = RecordingAdapter()
    result = await send(gateway, key, token, request(adapter, payload={"secret": "do not disclose"}))
    assert result.state == TerminalState.CANCELLED
    assert result.response is None
    assert result.safe_response["destination"] == "user:direct_support_stream"
    assert "do not disclose" not in json.dumps(result.safe_response)
    assert adapter.calls == []


@pytest.mark.asyncio
async def test_late_commit_is_deferred_until_green_or_yellow_recovery(tmp_path):
    gateway, key, token = make_gateway(tmp_path)

    async def commit_then_revoke(outbound):
        gateway.revoke(session_id=outbound_session, level=CrisisLevel.BLACK)
        return {"commit_id": "late-commit", "private_result": "hidden-during-crisis"}

    outbound_session = token.session_id
    adapter = RecordingAdapter(handler=commit_then_revoke)
    result = await send(gateway, key, token, request(
        adapter, destination="calendar:shared", capability="calendar:write",
        write=True, key="late-write",
    ))
    assert result.state == TerminalState.COMMITTED
    assert result.deferred is True
    assert result.response is None
    assert "hidden-during-crisis" not in json.dumps(result.safe_response)
    assert gateway.drain_deferred() == []
    gateway.recover(CrisisLevel.GREEN)
    drained = gateway.drain_deferred()
    assert len(drained) == 1
    assert drained[0].response["commit_id"] == "late-commit"
    assert gateway.drain_deferred() == []


@pytest.mark.asyncio
async def test_inflight_cancellation_hook_commits_cancelled_state(tmp_path):
    gateway, key, token = make_gateway(tmp_path)

    class CancellableAdapter(RecordingAdapter):
        def __init__(self):
            super().__init__()
            self.started = asyncio.Event()

        async def dispatch(self, outbound):
            self.calls.append(outbound)
            self.started.set()
            await asyncio.sleep(10)
            return {"should_not": "surface"}

        async def cancel(self, outbound):
            return True

    adapter = CancellableAdapter()
    outbound = request(adapter, destination="calendar:shared", capability="calendar:write",
                       write=True, key="cancel-write")
    task = asyncio.create_task(send(gateway, key, token, outbound))
    await adapter.started.wait()
    gateway.revoke(session_id=token.session_id, level=CrisisLevel.RED)
    result = await asyncio.wait_for(task, timeout=1)
    assert result.state == TerminalState.CANCELLED
    assert result.response is None
    assert gateway.store._rows["cancel-write"]["state"] == "CANCELLED"


@pytest.mark.asyncio
async def test_failed_adapter_without_status_is_unknown_not_guessed(tmp_path):
    gateway, key, token = make_gateway(tmp_path)

    async def fail(outbound):
        raise RuntimeError("network failed after dispatch")

    adapter = RecordingAdapter(handler=fail)
    result = await send(gateway, key, token, request(
        adapter, destination="calendar:shared", capability="calendar:write",
        write=True, key="unknown-write",
    ))
    assert result.state == TerminalState.UNKNOWN
    assert result.response is None


@pytest.mark.asyncio
async def test_status_hook_reconciles_committed_after_adapter_error(tmp_path):
    gateway, key, token = make_gateway(tmp_path)

    class StatusAdapter(RecordingAdapter):
        async def dispatch(self, outbound):
            self.calls.append(outbound)
            raise RuntimeError("lost response")

        async def status(self, outbound):
            return TerminalState.COMMITTED

    result = await send(gateway, key, token, request(
        StatusAdapter(), destination="calendar:shared", capability="calendar:write",
        write=True, key="status-write",
    ))
    assert result.state == TerminalState.COMMITTED


@pytest.mark.asyncio
async def test_none_consent_is_memory_only_even_if_disk_path_is_supplied(tmp_path):
    forbidden = tmp_path / "none-must-not-exist.sqlite3"
    gateway, key, token = make_gateway(tmp_path, consent=Consent.NONE, storage_path=str(forbidden))
    assert isinstance(gateway.store, MemoryReservationStore)
    adapter = RecordingAdapter()
    await send(gateway, key, token, request(adapter))
    assert gateway.ledger.records() == []
    assert not forbidden.exists()


def test_passive_single_user_autodrop_and_ten_user_cohort():
    local = AuditLedger(Consent.PASSIVE, local_single_user=True)
    deny("DENY_UNVERIFIED_ANONYMIZATION", local.record, "event", {"email": "a@example.com"},
         user_id="local-user")
    assert local.records() == []

    cohort = AuditLedger(Consent.PASSIVE, local_single_user=False)
    for index in range(9):
        assert cohort.record("event", {"email": "person@example.com"}, user_id=f"user-{index}") is False
    assert cohort.records() == []
    assert cohort.record("event", {"email": "person@example.com"}, user_id="user-9") is True
    records = cohort.records()
    assert len(records) == 1
    assert records[0]["cohort_size"] >= 10
    assert records[0]["window_hours"] == 24
    assert "details" not in records[0]
    assert "user_id" not in records[0]


def test_consent_downgrade_purges_cached_pending_records():
    ledger = AuditLedger(Consent.PASSIVE, local_single_user=False)
    ledger.record("pending", {}, user_id="one")
    assert ledger._pending
    ledger.update_consent(Consent.NONE)
    assert ledger._pending == {}
    assert ledger.record("ignored", {"private": True}, user_id="one") is False


def test_active_traces_require_encryption_and_never_store_plaintext(tmp_path):
    deny("AUDIT_ENCRYPTION_REQUIRED", AuditLedger, Consent.ACTIVE)
    path = tmp_path / "encrypted-audit.sqlite3"
    ledger = AuditLedger(Consent.ACTIVE, storage_path=str(path), encryption_key=Fernet.generate_key())
    ledger.record("private", {"note": "full-trace-secret"}, user_id="user")
    with sqlite3.connect(path) as connection:
        stored = connection.execute("SELECT payload FROM audit_ledger").fetchone()[0]
    assert "full-trace-secret" not in stored
    assert ledger.records()[0]["details"]["note"] == "full-trace-secret"


@pytest.mark.asyncio
async def test_sqlite_wal_releases_reservation_lock_during_adapter_io(tmp_path):
    path = tmp_path / "runtime.sqlite3"
    gateway, key, token = make_gateway(
        tmp_path, consent=Consent.ACTIVE, storage_path=str(path),
        audit_encryption_key=Fernet.generate_key(),
    )
    with sqlite3.connect(path) as connection:
        assert connection.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"

    started = asyncio.Event()
    release = asyncio.Event()

    async def slow_commit(outbound):
        started.set()
        await release.wait()
        return {"commit_id": "sqlite-commit"}

    adapter = RecordingAdapter(handler=slow_commit)
    task = asyncio.create_task(send(gateway, key, token, request(
        adapter, destination="calendar:shared", capability="calendar:write",
        write=True, key="sqlite-write",
    )))
    await started.wait()
    other = gateway.store.reserve("other-session-write", "other-session", "hash", token.exp)
    assert other.created is True
    release.set()
    result = await asyncio.wait_for(task, timeout=1)
    assert result.state == TerminalState.COMMITTED
    cached = await send(gateway, key, token, request(
        adapter, destination="calendar:shared", capability="calendar:write",
        write=True, key="sqlite-write",
    ))
    assert cached.cached is True
    assert len(adapter.calls) == 1


@pytest.mark.asyncio
async def test_every_write_requires_idempotency_key(tmp_path):
    gateway, key, token = make_gateway(tmp_path)
    adapter = RecordingAdapter()
    with pytest.raises(PolicyDenied) as caught:
        await send(gateway, key, token, request(
            adapter, destination="calendar:shared", capability="calendar:write", write=True,
        ))
    assert caught.value.code == "IDEMPOTENCY_KEY_REQUIRED"
    assert adapter.calls == []



@pytest.mark.asyncio
async def test_csg_rejects_omitted_lineage(tmp_path):
    """Test that CSG rejects requests with no provenance lineage."""
    gateway, key, token = make_gateway(tmp_path)
    adapter = RecordingAdapter()
    omitted = request(adapter, destination="calendar:shared", capability="calendar:write",
                      write=True, key="omitted-lineage")
    with pytest.raises(PolicyDenied) as caught:
        await gateway.dispatch(
            token, omitted,
            dpop_proof(key, omitted.method, omitted.url, token.token_id),
        )
    assert caught.value.code == "DENY_COMPOSITE_EGRESS"
    assert adapter.calls == []


@pytest.mark.asyncio
async def test_csg_rejects_reused_public_attestation(tmp_path):
    """Test that CSG rejects reused public provenance with unrelated payload."""
    gateway, key, token = make_gateway(tmp_path)
    adapter = RecordingAdapter()
    _, public = gateway.ingress.classify(
        {"public": "original"}, source_id="public", classification="public_external",
    )
    unrelated = request(adapter, destination="calendar:shared", capability="calendar:write",
                        write=True, key="reused-lineage", provenance=(public,),
                        payload={"private": "unrelated"})
    with pytest.raises(PolicyDenied) as caught:
        await gateway.dispatch(
            token, unrelated,
            dpop_proof(key, unrelated.method, unrelated.url, token.token_id),
        )
    assert caught.value.code == "DENY_COMPOSITE_EGRESS"
    assert adapter.calls == []


@pytest.mark.asyncio
async def test_mislabeled_side_effecting_post_still_requires_idempotency(tmp_path):
    gateway, key, token = make_gateway(tmp_path)
    adapter = RecordingAdapter()
    outbound = request(adapter, destination="calendar:shared", capability="calendar:write",
                       write=False, key=None)
    with pytest.raises(PolicyDenied) as caught:
        await send(gateway, key, token, outbound)
    assert caught.value.code == "IDEMPOTENCY_KEY_REQUIRED"
    assert adapter.calls == []


@pytest.mark.asyncio
async def test_inflight_nonwrite_response_is_cancelled_with_zero_disclosure(tmp_path):
    gateway, key, token = make_gateway(tmp_path)

    class CancellableResponse(RecordingAdapter):
        def __init__(self):
            super().__init__()
            self.started = asyncio.Event()

        async def dispatch(self, outbound):
            self.calls.append(outbound)
            self.started.set()
            await asyncio.sleep(10)
            return {"private": "must-not-surface"}

        async def cancel(self, outbound):
            return True

    adapter = CancellableResponse()
    task = asyncio.create_task(send(gateway, key, token, request(adapter)))
    await adapter.started.wait()
    gateway.revoke(session_id=token.session_id, level=CrisisLevel.BLACK)
    result = await asyncio.wait_for(task, timeout=1)
    assert result.state == TerminalState.CANCELLED
    assert result.response is None
    assert "must-not-surface" not in json.dumps(result.safe_response)


@pytest.mark.asyncio
async def test_active_response_is_encrypted_and_purged_on_passive_downgrade(tmp_path):
    path = tmp_path / "encrypted-responses.sqlite3"
    gateway, key, token = make_gateway(
        tmp_path, consent=Consent.ACTIVE, storage_path=str(path),
        audit_encryption_key=Fernet.generate_key(),
    )
    adapter = RecordingAdapter({"private": "response-body-secret"})
    outbound = request(adapter, destination="calendar:shared", capability="calendar:write",
                       write=True, key="encrypted-response")
    result = await send(gateway, key, token, outbound)
    assert result.response["private"] == "response-body-secret"
    with sqlite3.connect(path) as connection:
        stored = connection.execute(
            "SELECT response_json FROM reservations WHERE key = 'encrypted-response'",
        ).fetchone()[0]
    assert "response-body-secret" not in stored
    cached = await send(gateway, key, token, outbound)
    assert cached.response["private"] == "response-body-secret"

    gateway.update_consent(Consent.PASSIVE)
    with sqlite3.connect(path) as connection:
        assert connection.execute(
            "SELECT response_json FROM reservations WHERE key = 'encrypted-response'",
        ).fetchone()[0] is None


@pytest.mark.asyncio
async def test_passive_never_persists_full_response_but_never_reexecutes(tmp_path):
    gateway, key, token = make_gateway(
        tmp_path, consent=Consent.PASSIVE, local_single_user=False,
        storage_path=str(tmp_path / "passive.sqlite3"),
    )
    adapter = RecordingAdapter({"private": "not-retained"})
    outbound = request(adapter, destination="calendar:shared", capability="calendar:write",
                       write=True, key="passive-response")
    await send(gateway, key, token, outbound)
    cached = await send(gateway, key, token, outbound)
    assert cached.cached is True
    assert cached.response is None
    assert len(adapter.calls) == 1
    with sqlite3.connect(tmp_path / "passive.sqlite3") as connection:
        assert connection.execute(
            "SELECT response_json FROM reservations WHERE key = 'passive-response'",
        ).fetchone()[0] is None
