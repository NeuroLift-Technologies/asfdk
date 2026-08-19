"""RRT Advocate integration adapter, ported from
``@neurolift-technologies/asfdk`` (``src/integration/rrt.ts``).

⚠️ PROTOTYPE — NOT A SAFETY SYSTEM.

This adapter wraps ``rrt_advocate`` (the ``rrt-advocate`` distribution), an
**experimental** crisis-*detection* library with stubbed intervention layers. It
is **not medical advice, not a crisis service**, performs no real-time
monitoring, and **can miss real crisis signals**. Never rely on it as the sole
safety mechanism. If you or someone else needs help now, in the US call or text
**988** or chat https://988lifeline.org.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from rrt_advocate import CrisisAssessment, CrisisEngine, CrisisLevel

from ..prompt_defense import (
    RiskLevel,
    SanitizationResult,
    SecurityEvent,
    SecurityEventType,
    log_security_event,
    sanitize_input,
)
from ..types import Channel, normalize_channel

__all__ = [
    "CrisisLevel",
    "Channel",
    "CrisisAssessment",
    "assess",
    "get_status",
    "reset",
    "reset_session",
]

# One engine per user — the assessor scores user safety against per-user state,
# so engines are not shared across users.
_engines: Dict[str, CrisisEngine] = {}


def _get_engine(user_id: str) -> CrisisEngine:
    engine = _engines.get(user_id)
    if engine is None:
        engine = CrisisEngine(user_id)
        _engines[user_id] = engine
    return engine


@dataclass
class CrisisAssessmentWithProvenance:
    """Crisis assessment with channel provenance (D4).

    Extends the base CrisisAssessment with channel, trusted flag, and
    optional injection detection fields.
    """

    # Base assessment fields (from CrisisAssessment)
    timestamp: Any
    crisis_level: Any
    primary_indicators: List[str]
    secondary_indicators: List[str]
    confidence_score: float
    estimated_duration: Optional[float]
    recommended_interventions: List[str]
    escalation_threshold: float
    user_safety_score: float
    context_factors: Dict[str, Any] = field(default_factory=dict)

    # Provenance fields (D4)
    channel: Channel = Channel.UNKNOWN
    trusted: bool = False
    flagged: Optional[bool] = None
    flag_reason: Optional[str] = None


async def assess(
    user_id: str,
    input_text: str,
    channel: Optional[Channel] = None,
) -> CrisisAssessmentWithProvenance:
    """Run the 3-layer crisis-detection engine on a free-text input and return a
    :class:`CrisisAssessmentWithProvenance` (crisis level, safety score, recommended
    interventions).

    Security: Input is sanitized to prevent prompt injection attacks before assessment.

    Channel provenance (D4): the resolved channel and its derived ``trusted`` flag
    are recorded additively on the returned assessment. The assessment object is
    fresh per call, so provenance never bleeds between responses.

    Observe-phase caveat: the per-user engine is shared across channels, so an
    untrusted assessment may still mutate engine state here. Per-channel engines
    are deferred to Enforce; ``reset_session`` is the documented re-baseline hook
    Enforce will call when an untrusted assessment is discarded.

    :param user_id: The user the assessment is scored against.
    :param input_text: Free-text user input to assess.
    :param channel: Optional channel the interaction arrived on; absent → ``unknown``.
    """
    resolved = normalize_channel(channel)

    # Sanitize input before processing; a flagged result is logged but still
    # assessed defensively so a genuine crisis signal is never silently
    # suppressed by an injection heuristic (fail-open on detection).
    sanitization_result = sanitize_input(input_text)
    flagged = not sanitization_result.clean
    if flagged:
        log_security_event(
            SecurityEvent(
                event_type=(
                    SecurityEventType.INJECTION_ATTEMPT
                    if sanitization_result.risk_level == RiskLevel.HIGH
                    else SecurityEventType.VALIDATION_FAILURE
                ),
                user_id=user_id,
                details=sanitization_result.reason or "Input sanitization flagged in RRT assessment",
                timestamp=int(time.time() * 1000),
            )
        )

    assessment = _get_engine(user_id).assess(sanitization_result.content)

    # Build provenance-enriched result
    result = CrisisAssessmentWithProvenance(
        timestamp=assessment.timestamp,
        crisis_level=assessment.crisis_level,
        primary_indicators=assessment.primary_indicators,
        secondary_indicators=assessment.secondary_indicators,
        confidence_score=assessment.confidence_score,
        estimated_duration=assessment.estimated_duration,
        recommended_interventions=assessment.recommended_interventions,
        escalation_threshold=assessment.escalation_threshold,
        user_safety_score=assessment.user_safety_score,
        context_factors=assessment.context_factors,
        channel=resolved,
        trusted=resolved == Channel.USER_INPUT,
    )

    if flagged:
        result.flagged = True
        result.flag_reason = sanitization_result.reason

    return result


def get_status() -> Dict[str, Any]:
    """Return the active RRT Advocate component status."""
    return {"active": True, "mode": "crisis-detection"}


def reset(user_id: Optional[str] = None) -> None:
    """Reset per-session detector state. Pass a ``user_id`` to reset a single
    user's engine, or omit it to clear all cached engines.
    """
    if user_id is None:
        _engines.clear()
        return
    _engines.pop(user_id, None)


def reset_session(user_id: Optional[str] = None) -> None:
    """Re-baseline a single user's crisis-detection engine.

    Enforce-phase hook: call after discarding an untrusted assessment so engine
    state cannot carry it forward. Delegates to the engine's own
    ``reset_session()`` method (matching the TypeScript adapter, which calls
    ``getEngine(userId).resetSession()`` rather than destroying the engine).
    """
    if user_id is None:
        # No specific user to re-baseline; fall back to full clear so we never
        # create a phantom ''/None-keyed engine.
        reset()
        return
    _get_engine(user_id).reset_session()
