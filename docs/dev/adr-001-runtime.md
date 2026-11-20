# ADR-001 Python runtime integration (Draft)

This repository includes an **opt-in Python implementation slice** for the five runtime contracts summarized in `NLT-HND-2026-001`. It does not change ADR-001's Draft status or assert owner approval.

## Conformance boundary

- The normative `NLT-ADR-2026-001` v1.3.0 source and standalone AT-001 reference were not present in this repository or handoff. The implementation therefore follows the handoff's stated contracts, not an independently checked schema document.
- The integration is Python-only. TypeScript parity is not claimed.
- No concrete MCP/A2A client exists in this repository. `PolicyGateway.dispatch` wraps a generic asynchronous `OutboundAdapter`; production MCP/A2A clients must implement `dispatch`, and should implement `cancel` and `status` for deterministic reconciliation.
- Existing `create_foundation(user_id, mode)` behavior is unchanged. ADR enforcement is active only when `FoundationConfig.runtime` is supplied.

## Startup and dispatch

`RuntimeConfig` requires a signed `agent_charter.json`, a pinned public-JWK thumbprint for that charter, Sleepwalker capability limits, human-task grants, and a root adapter audience. Startup rejects missing, malformed, unpinned, or invalidly signed charters with `DENY_UNVERIFIED_PRINCIPAL`.

Callers mint a root ACDT using the SHA-256 JWK thumbprint of their DPoP key. Every outbound request must supply a fresh ES256 DPoP proof and pass this order of checks:

1. ACDT validity, `aud`, DPoP signature/claims/replay, and revocation.
2. Composite Synthesis Gate over **all** ingress contributors.
3. Required capability membership in `G_eff`.
4. Idempotent reservation for writes and short transaction finalization after dispatch.

No reservation or gateway lock is held across adapter I/O. Private note or unknown-taint contributors are allowed at `user:private_response`, but denied at shared destinations with `DENY_COMPOSITE_EGRESS` before the adapter is called. Every write requires an `idempotency_key`.

Ephemeral delegation requires a `user_decides` callback that returns exactly `True`. Delegation intersects human-task, parent, receiver, and Sleepwalker grants and decrements `rem_depth`; conflict-resolution strategies have no ability to expand this intersection.

## Revocation and support path

`revoke(..., level=CrisisLevel.RED/BLACK)` or the kill switch synchronously blocks new dispatch. Adapters with `cancel` can confirm in-flight cancellation. Failed dispatch uses `status` when available and otherwise resolves to `UNKNOWN`, never a guessed commit.

A commit racing with crisis revocation is stored as deferred. It is surfaced only by `drain_deferred()` after `recover(CrisisLevel.GREEN/YELLOW)`. RED/BLACK results use the isolated `SafeResponseHandler`, whose only destination is `user:direct_support_stream`; request payloads, adapter responses, credentials, and exceptions are not accepted by that handler.

## Consent and local state

- `NONE`: process-memory reservations/replay cache and no telemetry or SQLite file, even if a path is supplied.
- `PASSIVE`: PII redaction followed by a distinct-user, rolling 24-hour cohort gate (`k >= 10`). Persisted events contain aggregate cohort metadata only. Local single-user mode auto-drops with `DENY_UNVERIFIED_ANONYMIZATION`.
- `ACTIVE` / `EXPLICIT`: full traces require a caller-provided Fernet key and are encrypted before storage. Keys are not written by the runtime.

Other consent levels default to local SQLite WAL at `.asfdk/adr001.sqlite3`; set `storage_path` explicitly for an application-specific location. Consent downgrade clears pending/memory telemetry and persisted audit rows; switching to `NONE` also clears reservation/replay caches. Upgrading to full-trace consent requires reinitialization with an encryption key.

## Verification

`tests/test_adr001_runtime.py` covers AT-001A, AT-001B, DPoP replay and audience binding, idempotency, CSG precedence, revocation/cancellation/reconciliation, deferred commits, retention, encrypted traces, and SQLite lock release. All test keypairs are generated dynamically; no private keys are fixtures or persisted state.
