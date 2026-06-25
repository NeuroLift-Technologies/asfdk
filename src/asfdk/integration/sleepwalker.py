"""Sleepwalker Protocol integration adapter, ported from
``@neurolift-technologies/asfdk`` (``src/integration/sleepwalker.ts``).

Wraps ``sleepwalker_protocol`` (the ``sleepwalker-protocol`` distribution),
exposing a module-level singleton mirroring the TypeScript adapter.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from sleepwalker_protocol import EmotionalState, SleepwalkerProtocol

__all__ = [
    "EmotionalState",
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


def detect_emotional_state(
    user_input: str,
    session_history: Optional[List[Any]] = None,
) -> EmotionalState:
    """Classify the emotional state expressed in a user's free-text input."""
    return _get_instance().detect_emotional_state(user_input, session_history or [])


def assess_interaction(
    user_input: str,
    session_history: Optional[List[Any]] = None,
) -> Any:
    """Return a full interaction assessment object for the given input."""
    return _get_instance().assess_interaction(user_input, session_history or [])


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
