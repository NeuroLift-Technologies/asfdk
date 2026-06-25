"""The :class:`NeuroLiftFoundation` orchestrator, ported from
``@neurolift-technologies/asfdk`` (``src/foundation.ts``).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .integration import rrt, sleepwalker, toi_otoi
from .types import (
    ComponentStatus,
    FoundationComponents,
    FoundationConfig,
    FoundationMode,
    FoundationResponse,
    HealthCheckResult,
    InteractionType,
    UserInteraction,
)


@dataclass
class _ActiveComponents:
    toi: bool
    swp: bool
    rrt: bool


def _components_for_mode(
    mode: FoundationMode,
    overrides: Optional[FoundationComponents] = None,
) -> _ActiveComponents:
    defaults: Dict[FoundationMode, _ActiveComponents] = {
        FoundationMode.UNIFIED: _ActiveComponents(toi=True, swp=True, rrt=True),
        FoundationMode.CRISIS_ONLY: _ActiveComponents(toi=False, swp=False, rrt=True),
        FoundationMode.CONTINUITY_ONLY: _ActiveComponents(toi=False, swp=True, rrt=False),
        FoundationMode.FRAMEWORK_ONLY: _ActiveComponents(toi=True, swp=False, rrt=False),
        FoundationMode.DEVELOPMENT: _ActiveComponents(toi=True, swp=True, rrt=False),
    }
    base = defaults.get(mode, _ActiveComponents(toi=False, swp=False, rrt=False))

    def pick(override: Optional[bool], fallback: bool) -> bool:
        # Mirror TS ``override ?? fallback`` — None means "not provided".
        return fallback if override is None else override

    return _ActiveComponents(
        toi=pick(overrides.toi_otoi_framework if overrides else None, base.toi),
        swp=pick(overrides.sleepwalker_protocol if overrides else None, base.swp),
        rrt=pick(overrides.rrt_advocate if overrides else None, base.rrt),
    )


class NeuroLiftFoundation:
    """Central orchestrator for the Solidarity Framework.

    Routes user interactions to the active Solidarity Framework components
    (TOI-OTOI, Sleepwalker Protocol, RRT Advocate) according to the configured
    :class:`~asfdk.types.FoundationMode`.

    Obtain an instance via :func:`asfdk.create_foundation` rather than
    constructing directly.
    """

    def __init__(self, config: FoundationConfig) -> None:
        self._config = config
        self._active = _components_for_mode(config.mode, config.components)
        self._initialized = False

    async def initialize(self) -> None:
        """Mark the foundation as initialized. Called automatically by
        :func:`asfdk.create_foundation`.
        """
        self._initialized = True

    async def start(self) -> None:
        """Alias for :meth:`initialize`; ensures the foundation is ready before use."""
        if not self._initialized:
            await self.initialize()

    async def process_interaction(
        self, interaction: UserInteraction
    ) -> FoundationResponse:
        """Route a :class:`~asfdk.types.UserInteraction` to the appropriate active
        components and return a :class:`~asfdk.types.FoundationResponse` with
        aggregated content.

        - ``EMOTIONAL_ASSESSMENT`` → Sleepwalker Protocol (+ RRT handoff if crisis indicated)
        - ``PREFERENCE_UPDATE`` → TOI-OTOI schema validation
        - ``CRISIS_ALERT`` / ``EMERGENCY_ESCALATION`` → RRT Advocate crisis detection
        - All other types → empty ``components_involved`` list with ``success=True``
        """
        components: List[str] = []
        content: Dict[str, Any] = {}

        if (
            self._active.swp
            and interaction.interaction_type == InteractionType.EMOTIONAL_ASSESSMENT
        ):
            try:
                user_input = str(
                    (interaction.data or {}).get("text", "")
                    if (interaction.data or {}).get("text") is not None
                    else ""
                )
                state = sleepwalker.detect_emotional_state(user_input)
                content["emotionalState"] = state

                if self._active.rrt and sleepwalker.requires_rrta_handoff(state):
                    # Own error boundary so an RRT failure is attributed to
                    # rrt_advocate (not sleepwalker) and does not discard the
                    # emotional-state result.
                    try:
                        content["rrt"] = await rrt.assess(
                            self._config.user_id, user_input
                        )
                    except Exception as err:  # noqa: BLE001
                        content["error"] = {
                            "component": "rrt_advocate",
                            "message": str(err),
                        }
                    # Listed whenever attempted (success or failure), consistent
                    # with the crisis/emergency route and with sleepwalker_protocol.
                    components.append("rrt_advocate")
            except Exception as err:  # noqa: BLE001
                content["error"] = {
                    "component": "sleepwalker_protocol",
                    "message": str(err),
                }
            components.append("sleepwalker_protocol")

        if (
            self._active.toi
            and interaction.interaction_type == InteractionType.PREFERENCE_UPDATE
        ):
            content["toiValidation"] = toi_otoi.validate_toi(
                (interaction.data or {}).get("toi")
            )
            components.append("toi_otoi_framework")

        if self._active.rrt and interaction.interaction_type in (
            InteractionType.CRISIS_ALERT,
            InteractionType.EMERGENCY_ESCALATION,
        ):
            user_input = str(
                (interaction.data or {}).get("text", "")
                if (interaction.data or {}).get("text") is not None
                else ""
            )
            # Error boundary: an RRT failure must not abort a crisis/emergency route.
            try:
                content["rrt"] = await rrt.assess(self._config.user_id, user_input)
            except Exception as err:  # noqa: BLE001
                content["error"] = {"component": "rrt_advocate", "message": str(err)}
            components.append("rrt_advocate")

        return FoundationResponse(
            timestamp=datetime.now(),
            response_type=interaction.interaction_type.value
            if isinstance(interaction.interaction_type, InteractionType)
            else str(interaction.interaction_type),
            content=content,
            components_involved=components,
            success=True,
        )

    async def assess_emotional_state(
        self,
        input: str,
        _context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Assess the emotional state of a free-text input via the Sleepwalker
        Protocol. Returns ``None`` when Sleepwalker is not active for the current
        mode.

        :param input: Free-text user input to assess.
        :param _context: Reserved for future context enrichment; currently unused.
        """
        if not self._active.swp:
            return None
        return sleepwalker.assess_interaction(input)

    async def update_preferences(self, prefs: Dict[str, Any]) -> None:
        """Validate a preference object against the TOI schema and raise if
        invalid. No-op when TOI-OTOI is not active for the current mode.

        :raises ValueError: If the preference object fails TOI schema validation.
        """
        if self._active.toi:
            result = toi_otoi.validate_toi(prefs)
            if not result.valid:
                errors = [
                    {"message": e.message, "path": e.path, "code": e.code}
                    for e in (result.errors or [])
                ]
                raise ValueError(
                    "TOI validation failed: " + json.dumps(errors, separators=(",", ":"))
                )

    def get_system_status(self) -> Dict[str, Any]:
        """Return the current mode, user_id, initialization state, and
        per-component status.
        """
        return {
            "mode": self._config.mode,
            "userId": self._config.user_id,
            "initialized": self._initialized,
            "components": {
                "toi_otoi_framework": toi_otoi.get_status()
                if self._active.toi
                else {"active": False, "mode": "disabled"},
                "sleepwalker_protocol": sleepwalker.get_status()
                if self._active.swp
                else {"active": False, "mode": "disabled"},
                "rrt_advocate": rrt.get_status()
                if self._active.rrt
                else {"active": False, "mode": "disabled"},
            },
        }

    async def health_check(self) -> HealthCheckResult:
        """Return a structured health report for all components, reflecting which
        are active for the current :class:`~asfdk.types.FoundationMode`.
        """
        return HealthCheckResult(
            healthy=True,
            timestamp=datetime.now(),
            components={
                "toi_otoi_framework": ComponentStatus(active=True, mode="toi-otoi-validation")
                if self._active.toi
                else ComponentStatus(active=False, mode="disabled"),
                "sleepwalker_protocol": ComponentStatus(active=True, mode="emotional-continuity")
                if self._active.swp
                else ComponentStatus(active=False, mode="disabled"),
                "rrt_advocate": ComponentStatus(active=True, mode="crisis-detection")
                if self._active.rrt
                else ComponentStatus(active=False, mode="disabled"),
            },
        )

    async def shutdown(self) -> None:
        """Reset Sleepwalker and RRT Advocate state and mark the foundation as
        uninitialized.
        """
        sleepwalker.reset()
        rrt.reset(self._config.user_id)
        self._initialized = False


__all__ = ["NeuroLiftFoundation"]
