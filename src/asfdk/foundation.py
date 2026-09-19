"""The :class:`NeuroLiftFoundation` orchestrator, ported from
``@neurolift-technologies/asfdk`` (``src/foundation.ts``).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

try:  # ``nlt-toi`` >= 1.0.0 ships this alias; keep annotations meaningful either way.
    from nlt_toi import ToiDocument
except ImportError:  # pragma: no cover - defensive
    ToiDocument = Dict[str, Any]  # type: ignore[misc,assignment]

from .integration import rrt, sleepwalker, toi_otoi
from .toi_bootstrap import generator_source, get_generator_class
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
        #: The foundation's active ``.toi`` document, generated before any
        #: component activates (see :meth:`initialize`). ``None`` until
        #: initialization succeeds.
        self._toi_document: Optional[ToiDocument] = None

    async def initialize(self) -> None:
        """Bootstrap the foundation.

        The TOI generator runs *first*: the foundation's active document is
        generated/validated from the configured source (or privacy-first
        defaults) and stored before any component becomes active. A failure to
        generate a conforming document raises and leaves the foundation
        uninitialized (fail-loud), so components are never activated against a
        broken or absent TOI.
        """
        self._toi_document = self._generate_toi()
        self._initialized = True

    def _generate_toi(self) -> ToiDocument:
        """Run the ``toi-generator`` logic over the configured source.

        The authoring helper is the pillar's own ``TOIDocumentGenerator`` when the
        installed ``nlt-toi`` provides it, otherwise the local mirror in
        :mod:`asfdk.toi_bootstrap` (which delegates validation to the pillar's
        canonical schema). :func:`asfdk.toi_bootstrap.generator_source` reports
        which one is in use.

        Source resolution:
        - ``None``  → privacy-first document generated from defaults
        - ``str``   → path to a ``.toi``/``.json`` file, parsed then regenerated
        - ``dict``  → partial preferences or a full document, merged over defaults

        Every path validates through the canonical schema before returning, so
        an invalid source raises here rather than activating a broken TOI.
        """
        generator = get_generator_class()
        source = self._config.toi
        if source is None:
            return generator.from_defaults("anonymous").document
        if isinstance(source, dict):
            return generator.from_dict(source).document
        if isinstance(source, str):
            with open(source, encoding="utf-8") as handle:
                raw = json.load(handle)
            if not isinstance(raw, dict):
                raise TypeError("a .toi source file must contain a JSON object")
            return generator.from_dict(raw).document
        raise TypeError(
            "toi must be a preferences dict, a path to a .toi/.json file, or None; "
            f"got {type(source).__name__}"
        )

    def get_active_toi(self) -> Optional[ToiDocument]:
        """Return the foundation's active TOI document, or ``None`` before
        :meth:`initialize` succeeds."""
        return self._toi_document

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

        # Provenance (D2/D4/D6): resolve the channel from the TOP-LEVEL field
        # only — values nested inside data/context are ignored for trust
        # (anti-spoofing). Absent → ``unknown``; trusted := channel == user_input.
        channel = normalize_channel(interaction.channel)
        trusted = channel == Channel.USER_INPUT
        # D5 gate-up predicate: untrusted channel AND high-severity crisis signal.
        high_severity = False
        if (
            self._active.swp
            and interaction.interaction_type == InteractionType.EMOTIONAL_ASSESSMENT
        ):
            try:
                text_val = (interaction.data or {}).get("text")
                user_input = str(text_val) if text_val is not None else ""
                state = sleepwalker.detect_emotional_state(
                    user_input, [], channel, self._config.user_id
                )
                # Emotional-path high-severity: explicit crisis flags on the state.
                high_severity = bool(
                    state.explicit_suicidal_ideation
                    or state.self_harm_indicators
                    or state.inability_to_ensure_safety
                )
                content["emotionalState"] = state

                if self._active.rrt and sleepwalker.requires_rrta_handoff(state):
                    # Own error boundary so an RRT failure is attributed to
                    # rrt_advocate (not sleepwalker) and does not discard the
                    # emotional-state result.
                    try:
                        content["rrt"] = await rrt.assess(
                            self._config.user_id, user_input, channel
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
            text_val = (interaction.data or {}).get("text")
            user_input = str(text_val) if text_val is not None else ""
            # Error boundary: an RRT failure must not abort a crisis/emergency route.
            try:
                content["rrt"] = await rrt.assess(
                    self._config.user_id, user_input, channel
                )
                # CRISIS_ALERT is high-severity only on an actual RED/BLACK
                # reading; a failed detection is not evidence of severity, so it
                # does not gate up.
                if interaction.interaction_type == InteractionType.CRISIS_ALERT:
                    level = getattr(content.get("rrt"), "crisis_level", None)
                    high_severity = level in (
                        rrt.CrisisLevel.RED,
                        rrt.CrisisLevel.BLACK,
                    )
            except Exception as err:  # noqa: BLE001
                content["error"] = {"component": "rrt_advocate", "message": str(err)}
            components.append("rrt_advocate")

        # D5 high-severity fallbacks:
        # - EMERGENCY_ESCALATION is always high-severity.
        # - CRISIS_ALERT with RRT inactive is high-severity by interaction type
        #   alone (fail-safe: never silently ignored when detection is off).
        if interaction.interaction_type == InteractionType.EMERGENCY_ESCALATION:
            high_severity = True
        if (
            interaction.interaction_type == InteractionType.CRISIS_ALERT
            and not self._active.rrt
        ):
            high_severity = True

        # D5 gate-up (Enforce): an untrusted channel carrying a high-severity
        # signal is the one combination that escalates rather than degrades.
        content["channel"] = channel
        content["trusted"] = trusted
        content["gateUp"] = not trusted and high_severity

        return FoundationResponse(
            timestamp=datetime.now(timezone.utc),
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
        channel: Optional[Channel] = None,
    ) -> Any:
        """Assess the emotional state of a free-text input via the Sleepwalker
        Protocol. Returns ``None`` when Sleepwalker is not active for the current
        mode.

        Channel provenance (D4): the resolved channel and its derived ``trusted``
        flag are recorded additively on the returned assessment — no envelope —
        so existing consumers see the same shape plus ``channel``, ``trusted``,
        and ``gateUp`` properties. Absent channel → ``unknown``/untrusted.

        :param input: Free-text user input to assess.
        :param _context: Reserved for future context enrichment; currently unused.
        :param channel: Optional channel the interaction arrived on; absent → ``unknown``.
        """
        if not self._active.swp:
            return None
        resolved = normalize_channel(channel)
        trusted = resolved == Channel.USER_INPUT

        def _get(obj: Any, name: str, default: Any = None) -> Any:
            value = obj.get(name, default) if isinstance(obj, dict) else getattr(obj, name, default)
            return default if value is None else value

        result = sleepwalker.assess_interaction(input)
        # assessInteraction nests the state; read the crisis flags from it
        # (falling back to the top level for flat-shaped callers).
        inner = _get(result, "emotional_state", None) or _get(
            result, "emotionalState", None
        )
        if inner is None:
            inner = result
        high_severity = bool(
            _get(inner, "explicit_suicidal_ideation", False)
            or _get(inner, "explicitSuicidalIdeation", False)
            or _get(inner, "self_harm_indicators", False)
            or _get(inner, "selfHarmIndicators", False)
            or _get(inner, "inability_to_ensure_safety", False)
            or _get(inner, "inabilityToEnsureSafety", False)
        )
        gate_up = not trusted and high_severity
        if isinstance(result, dict):
            result["channel"] = resolved
            result["trusted"] = trusted
            result["gateUp"] = gate_up
        else:
            result.channel = resolved
            result.trusted = trusted
            result.gateUp = gate_up
        return result

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
            "toi": {
                "generated": self._toi_document is not None,
                # ``"nlt_toi"`` when the pillar supplies the authoring helper,
                # otherwise ``"asfdk-fallback"`` — the fallback is never silent.
                "generator": generator_source(),
                "document": self._toi_document,
            },
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
            timestamp=datetime.now(timezone.utc),
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
