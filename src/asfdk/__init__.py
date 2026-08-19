"""``asfdk`` — the Agent Solidarity Framework Development Kit.

ASFDK is the Python umbrella over the four Solidarity Framework pillars, ported
from ``@neurolift-technologies/asfdk``. The :class:`NeuroLiftFoundation`
orchestrator is the high-level entry point; the four pillar packages are also
re-exported as namespaces so a single install surfaces every layer:

- ``toi``         → ``nlt_toi`` (Terms of Interaction — user preferences)
- ``otoi``        → ``nlt_otoi`` (Orchestrated TOI — multi-agent honoring)
- ``rrt``         → ``rrt_advocate`` (crisis detection — ⚠️ prototype)
- ``sleepwalker`` → ``sleepwalker_protocol`` (emotional continuity)

Example::

    import asyncio
    from asfdk import create_foundation, FoundationMode, toi

    async def main():
        foundation = await create_foundation("user-123", FoundationMode.UNIFIED)
        result = toi.safe_parse_toi(my_preferences)

    asyncio.run(main())
"""
from __future__ import annotations

# The four Solidarity Framework pillars, re-exported as namespaces (mirrors the
# TypeScript ``export * as toi from '@neurolift-technologies/toi'`` lines).
import nlt_otoi as otoi
import nlt_toi as toi
import rrt_advocate as rrt
import sleepwalker_protocol as sleepwalker

# High-level orchestrator (primary API).
from .create_foundation import create_foundation
from .foundation import NeuroLiftFoundation
from .types import (
    Channel,
    ComponentStatus,
    FoundationComponents,
    FoundationConfig,
    FoundationMode,
    FoundationResponse,
    HealthCheckResult,
    InteractionType,
    UserInteraction,
    normalize_channel,
)

# Prompt defense utilities (security layer).
from .prompt_defense import (
    RiskLevel,
    SanitizationResult,
    SecurityEvent,
    SecurityEventType,
    ValidationResult,
    create_secure_system_prompt,
    detect_injection_patterns,
    log_security_event,
    sanitize_input,
    validate_input_length,
    validate_output,
)

__version__ = "0.3.0"

__all__ = [
    # high-level orchestrator
    "create_foundation",
    "NeuroLiftFoundation",
    # types
    "FoundationMode",
    "InteractionType",
    "Channel",
    "normalize_channel",
    "FoundationConfig",
    "FoundationComponents",
    "UserInteraction",
    "FoundationResponse",
    "ComponentStatus",
    "HealthCheckResult",
    # prompt defense (security layer)
    "RiskLevel",
    "SecurityEventType",
    "SanitizationResult",
    "ValidationResult",
    "SecurityEvent",
    "detect_injection_patterns",
    "validate_input_length",
    "sanitize_input",
    "validate_output",
    "create_secure_system_prompt",
    "log_security_event",
    # pillar namespaces
    "toi",
    "otoi",
    "rrt",
    "sleepwalker",
    "__version__",
]
