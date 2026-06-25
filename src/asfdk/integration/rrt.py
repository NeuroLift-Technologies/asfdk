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

from typing import Any, Dict, Optional

from rrt_advocate import CrisisAssessment, CrisisEngine, CrisisLevel

__all__ = [
    "CrisisLevel",
    "CrisisAssessment",
    "assess",
    "get_status",
    "reset",
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


async def assess(user_id: str, input: str) -> CrisisAssessment:
    """Run the 3-layer crisis-detection engine on a free-text input and return a
    :class:`CrisisAssessment` (crisis level, safety score, recommended
    interventions).

    Declared ``async`` to mirror the TypeScript adapter's signature; the
    underlying Python engine call is synchronous.

    :param user_id: The user the assessment is scored against.
    :param input: Free-text user input to assess.
    """
    return _get_engine(user_id).assess(input)


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
