"""Sleepwalker Protocol integration adapter, ported from
``@neurolift-technologies/asfdk`` (``src/integration/sleepwalker.ts``).

Wraps ``sleepwalker_protocol`` (the ``sleepwalker-protocol`` distribution),
exposing a module-level singleton mirroring the TypeScript adapter.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from sleepwalker_protocol import EmotionalState, SleepwalkerProtocol

from ..prompt_defense import (
    RiskLevel,
    SecurityEvent,
    SecurityEventType,
    log_security_event,
    sanitize_input,
)
from ..types import Channel, normalize_channel

__all__ = [
    "EmotionalState",
    "EmotionalStateWithProvenance",
    "Channel",
    "detect_emotional_state",
    "assess_interaction",
    "requires_rrta_handoff",
    "get_status",
    "reset",
]

_instance: Optional[SleepwalkerProtocol] = None


def _get_instance() -> SleepwalkerProtocol:
    global _instance
    if _instance is None:
        _instance = SleepwalkerProtocol(logging_enabled=False)
    return _instance


@dataclass
class EmotionalStateWithProvenance:
    """Emotional state with channel provenance (D4).

    Extends the base EmotionalState with channel, trusted flag, and
    optional injection detection fields.
    """

    # Base emotional state fields
    state: str
    confidence: float
    indicators: List[str] = field(default_factory=list)
    raw_scores: Dict[str, float] = field(default_factory=dict)

    # Provenance fields (D4)
    channel: Channel = Channel.UNKNOWN
    trusted: bool = False
    flagged: Optional[bool] = None
    flag_reason: Optional[str] = None


def detect_emotional_state(
    user_input: str,
    session_history: Optional[List[Any]] = None,
    channel: Optional[Channel] = None,
    user_id: str = "unknown",
) -> EmotionalStateWithProvenance:
    """Classify the emotional state expressed in a user's free-text input.

    The resolved channel and its derived ``trusted`` flag are recorded additively
    on the returned state (absent channel → ``unknown``).

    Security: Input is sanitized to prevent prompt injection attacks.

    :param user_input: Free-text user input to assess.
    :param session_history: Optional list of previous interactions for context.
    :param channel: Optional channel the interaction arrived on; absent → ``unknown``.
    :param user_id: The user identifier for security logging.
    """
    resolved = normalize_channel(channel)

    # Sanitize input before processing; a flagged result is logged but still
    # assessed defensively so a genuine signal is never silently suppressed by
    # an injection heuristic (fail-open on detection).
    sanitization_result = sanitize_input(user_input)
    flagged = not sanitization_result.clean
    if flagged:
        log_security_event(
            SecurityEvent(
                event_type=(
                    SecurityEventType.INJECTION_ATTEMPT
                    if sanitization_result.risk_level == RiskLevel.HIGH
                    else SecurityEventType.LENGTH_EXCEEDED
                    if sanitization_result.risk_level == RiskLevel.MEDIUM
                    else SecurityEventType.VALIDATION_FAILURE
                ),
                user_id=user_id,
                details=sanitization_result.reason or "Input sanitization flagged in Sleepwalker assessment",
                timestamp=int(time.time() * 1000),
            )
        )

    state = _get_instance().detect_emotional_state(
        sanitization_result.content, session_history or []
    )

    # Build provenance-enriched result
    result = EmotionalStateWithProvenance(
        state=state.state if hasattr(state, "state") else str(state),
        confidence=state.confidence if hasattr(state, "confidence") else 0.0,
        indicators=state.indicators if hasattr(state, "indicators") else [],
        raw_scores=state.raw_scores if hasattr(state, "raw_scores") else {},
        channel=resolved,
        trusted=resolved == Channel.USER_INPUT,
    )

    if flagged:
        result.flagged = True
        result.flag_reason = sanitization_result.reason

    return result


def assess_interaction(
    user_input: str,
    session_history: Optional[List[Any]] = None,
    channel: Optional[Channel] = None,
    user_id: str = "unknown",
) -> Any:
    """Return a full interaction assessment object for the given input.

    The resolved channel and its derived ``trusted`` flag are recorded additively
    on the returned assessment (absent channel → ``unknown``).

    Security: Input is sanitized to prevent prompt injection attacks before
    assessment, matching the ``detect_emotional_state`` flow.
    """
    resolved = normalize_channel(channel)

    # Sanitize input before processing; same fail-open policy as detect_emotional_state.
    sanitization_result = sanitize_input(user_input)
    flagged = not sanitization_result.clean
    if flagged:
        log_security_event(
            SecurityEvent(
                event_type=(
                    SecurityEventType.INJECTION_ATTEMPT
                    if sanitization_result.risk_level == RiskLevel.HIGH
                    else SecurityEventType.LENGTH_EXCEEDED
                    if sanitization_result.risk_level == RiskLevel.MEDIUM
                    else SecurityEventType.VALIDATION_FAILURE
                ),
                user_id=user_id,
                details=sanitization_result.reason or "Input sanitization flagged in Sleepwalker assess_interaction",
                timestamp=int(time.time() * 1000),
            )
        )

    result = _get_instance().assess_interaction(
        sanitization_result.content, session_history or []
    )

    # Add provenance to result if it's a dict-like object
    if isinstance(result, dict):
        result["channel"] = resolved.value
        result["trusted"] = resolved == Channel.USER_INPUT
        if flagged:
            result["flagged"] = True
            result["flag_reason"] = sanitization_result.reason
    elif hasattr(result, "__dict__"):
        result.channel = resolved
        result.trusted = resolved == Channel.USER_INPUT
        if flagged:
            result.flagged = True
            result.flag_reason = sanitization_result.reason

    return result


def requires_rrta_handoff(state: EmotionalState) -> bool:
    """Return ``True`` when the assessed emotional state warrants an RRT Advocate handoff."""
    return _get_instance().requires_rrta_handoff(state)


def get_status() -> Dict[str, Any]:
    """Return the active Sleepwalker Protocol component status."""
    return {"active": True, "mode": "emotional-continuity"}


def reset() -> None:
    """Reset the singleton instance; called during :meth:`NeuroLiftFoundation.shutdown`."""
    global _instance
    _instance = None
