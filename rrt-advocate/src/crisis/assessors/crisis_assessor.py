"""
Crisis Assessor - Assesses crisis severity and context

Consumes the ``CrisisSignal`` objects produced by :class:`CrisisDetector` and
produces a :class:`CrisisAssessment`. The assessment logic is deterministic and
explainable: severity is derived from the strongest matched indicator, with
explicit, safety-first escalation for suicidal-ideation signals.

This complements the lexical baseline detector and inherits its caveats — it is
a transparent default, not a clinical instrument. See the safety note in
``crisis/detectors/crisis_detector.py``.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class CrisisLevel(Enum):
    """Crisis severity levels"""
    GREEN = "stable"
    YELLOW = "elevated"
    ORANGE = "high"
    RED = "critical"
    BLACK = "emergency"


@dataclass
class CrisisAssessment:
    """Comprehensive crisis assessment"""
    timestamp: datetime
    crisis_level: CrisisLevel
    primary_indicators: list[str]
    secondary_indicators: list[str]
    confidence_score: float
    estimated_duration: timedelta | None
    recommended_interventions: list[str]
    escalation_threshold: float
    user_safety_score: float
    context_factors: dict[str, Any]


# Intervention suggestions per indicator name. Kept as data so the mapping is
# reviewable and adopters can extend it without touching control flow.
_INTERVENTIONS: dict[str, list[str]] = {
    "suicidal_thoughts": ["safety_planning", "crisis_hotline_988", "emergency_stabilization"],
    "panic_symptoms": ["grounding_exercise", "breathing_guidance"],
    "overwhelm": ["task_breakdown", "grounding_exercise"],
    "stress_level": ["breathing_guidance", "supportive_check_in"],
    "isolation": ["connection_prompt", "supportive_check_in"],
    "substance_abuse": ["harm_reduction_resources", "supportive_check_in"],
    "sleep_disturbance": ["sleep_hygiene_tips", "supportive_check_in"],
    "appetite_change": ["nutrition_check_in", "supportive_check_in"],
}

# Intensity bands → level for the general (non-suicidal) case.
_PRIMARY_INTENSITY = 0.6  # at/above this an indicator is "primary"


class CrisisAssessor:
    """Assesses crisis severity and context."""

    def __init__(self, user_id: str, thresholds: dict[str, float] | None = None):
        self.user_id = user_id
        self.thresholds = thresholds or {}
        self.logger = logging.getLogger(f"CrisisAssessor-{user_id}")

    async def assess_crisis(self, indicators: list[Any]) -> CrisisAssessment:
        """Assess crisis based on detected indicators.

        ``indicators`` is a list of ``CrisisSignal``-like objects exposing
        ``indicator`` (an enum or object with ``.value``), ``intensity`` and
        ``confidence`` attributes. An empty list yields the safe default
        (GREEN, zero confidence, full safety score).
        """
        if not indicators:
            return self._safe_default()

        top_intensity = 0.0
        max_confidence = 0.0
        suicidal_intensity = 0.0
        primary: list[str] = []
        secondary: list[str] = []
        recommended: list[str] = []
        seen_interventions = set()

        for signal in indicators:
            name = self._indicator_name(signal)
            intensity = float(getattr(signal, "intensity", 0.0) or 0.0)
            confidence = float(getattr(signal, "confidence", 0.0) or 0.0)

            top_intensity = max(top_intensity, intensity)
            max_confidence = max(max_confidence, confidence)
            if name == "suicidal_thoughts":
                suicidal_intensity = max(suicidal_intensity, intensity)

            if intensity >= _PRIMARY_INTENSITY:
                primary.append(name)
            else:
                secondary.append(name)

            for intervention in _INTERVENTIONS.get(name, ["supportive_check_in"]):
                if intervention not in seen_interventions:
                    seen_interventions.add(intervention)
                    recommended.append(intervention)

        crisis_level = self._derive_level(top_intensity, suicidal_intensity)
        user_safety_score = self._safety_score(crisis_level, top_intensity, suicidal_intensity)

        self.logger.info(
            "Assessed crisis for %s: level=%s confidence=%.2f indicators=%s",
            self.user_id, crisis_level.value, max_confidence, primary + secondary,
        )

        return CrisisAssessment(
            timestamp=datetime.now(),
            crisis_level=crisis_level,
            primary_indicators=primary,
            secondary_indicators=secondary,
            confidence_score=round(max_confidence, 3),
            estimated_duration=None,
            recommended_interventions=recommended,
            escalation_threshold=self.thresholds.get("suicidal_thoughts", 0.8),
            user_safety_score=round(user_safety_score, 3),
            context_factors={
                "top_intensity": round(top_intensity, 3),
                "suicidal_intensity": round(suicidal_intensity, 3),
            },
        )

    @staticmethod
    def _derive_level(top_intensity: float, suicidal_intensity: float) -> CrisisLevel:
        """Map intensities to a crisis level, escalating safety-first.

        Suicidal-ideation signals never resolve below RED, and a strong one
        goes straight to BLACK regardless of other indicators.
        """
        if suicidal_intensity >= 0.9:
            return CrisisLevel.BLACK
        if suicidal_intensity > 0.0:
            return CrisisLevel.RED
        if top_intensity >= 0.85:
            return CrisisLevel.RED
        if top_intensity >= 0.65:
            return CrisisLevel.ORANGE
        if top_intensity >= 0.4:
            return CrisisLevel.YELLOW
        return CrisisLevel.GREEN

    @staticmethod
    def _safety_score(level: CrisisLevel, top_intensity: float, suicidal_intensity: float) -> float:
        """Lower score = greater safety concern.

        Suicidal signals drive the score below the RRT Advocate's emergency
        threshold (0.3) so the pipeline routes to emergency escalation.
        """
        if suicidal_intensity > 0.0 or level == CrisisLevel.BLACK:
            return max(0.0, 0.2 - suicidal_intensity * 0.1)
        return max(0.0, 1.0 - top_intensity)

    @staticmethod
    def _indicator_name(signal: Any) -> str:
        """Best-effort extraction of an indicator's string name."""
        indicator = getattr(signal, "indicator", signal)
        return getattr(indicator, "value", str(indicator))

    @staticmethod
    def _safe_default() -> CrisisAssessment:
        return CrisisAssessment(
            timestamp=datetime.now(),
            crisis_level=CrisisLevel.GREEN,
            primary_indicators=[],
            secondary_indicators=[],
            confidence_score=0.0,
            estimated_duration=None,
            recommended_interventions=[],
            escalation_threshold=0.8,
            user_safety_score=1.0,
            context_factors={},
        )
