"""Shared types for the ADR-001 Python runtime."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, FrozenSet, Optional, Protocol, Tuple, runtime_checkable


class Consent(str, Enum):
    NONE = "NONE"
    PASSIVE = "PASSIVE"
    ACTIVE = "ACTIVE"
    EXPLICIT = "EXPLICIT"


class CrisisLevel(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"
    BLACK = "BLACK"


class TerminalState(str, Enum):
    CANCELLED = "CANCELLED"
    COMMITTED = "COMMITTED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Provenance:
    classification: str
    source_id: str
    no_derived_egress: bool = True
    content_hash: str = ""
    attestation: str = field(default="", repr=False)


@dataclass(frozen=True)
class SynthesizedContent:
    content_hash: str
    provenance: Tuple[Provenance, ...]
    attestation: str = field(default="", repr=False)


@dataclass(frozen=True)
class ACDT:
    token_id: str
    subject: str
    audience: str
    capabilities: FrozenSet[str]
    rem_depth: int
    exp: float
    cnf_jkt: str
    session_id: str
    handoff_id: str
    lineage_hash: str
    parent_token_id: Optional[str] = None


@dataclass(frozen=True)
class OperationDefinition:
    """Trusted operation metadata registered by the gateway owner."""
    name: str
    method: str
    url: str
    audience: str
    destination: str
    required_capability: str
    boundary: str = "tool"
    is_write: bool = False


@dataclass(frozen=True)
class OutboundRequest:
    adapter: OutboundAdapter
    method: str
    url: str
    audience: str
    destination: str
    payload: Any
    provenance: Tuple[Provenance, ...] = ()
    required_capability: str = ""
    boundary: str = "tool"
    write: bool = False
    idempotency_key: Optional[str] = None
    synthesis: Optional[SynthesizedContent] = None
    operation: str = ""


@dataclass(frozen=True)
class DispatchResult:
    state: TerminalState
    response: Any = None
    deferred: bool = False
    cached: bool = False
    safe_response: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class Reservation:
    key: str
    session_id: str
    request_hash: str
    state: str
    response: Any = None
    deferred: bool = False
    created: bool = False


@runtime_checkable
class OutboundAdapter(Protocol):
    async def dispatch(self, request: OutboundRequest) -> Any:
        """Execute the request after the gateway has authorized it."""


@runtime_checkable
class StatusAdapter(Protocol):
    async def status(self, request: OutboundRequest) -> TerminalState:
        """Return a terminal state, never a best-effort guess."""


@runtime_checkable
class CancellationAdapter(Protocol):
    async def cancel(self, request: OutboundRequest) -> bool:
        """Return true only when the adapter confirms cancellation."""


@dataclass
class RuntimeConfig:
    charter_path: str
    trusted_charter_keys: Dict[str, str]
    sleepwalker_capabilities: FrozenSet[str]
    consent: Consent = Consent.NONE
    storage_path: Optional[str] = None
    local_single_user: bool = True
    audit_encryption_key: Optional[bytes] = field(default=None, repr=False)
    human_task_capabilities: FrozenSet[str] = frozenset()
    root_audience: str = ""
    root_depth: int = 0
    root_session_id: str = "default"


__all__ = [
    "ACDT", "CancellationAdapter", "Consent", "CrisisLevel", "DispatchResult",
    "OperationDefinition", "OutboundAdapter", "OutboundRequest", "Provenance",
    "Reservation", "RuntimeConfig", "StatusAdapter", "SynthesizedContent", "TerminalState",
]
