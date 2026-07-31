"""
Crisis Assessor

Maps the aggregated ``CrisisIndicators`` produced by the 3-layer CrisisDetector
to a ``CrisisAssessment``. This is a port of the canonical rrt-advocate assessor
(NeuroLift-Technologies/rrt-advocate), kept domain-neutral for ASFDK: it relies
only on the aggregate confidence and the layer signals, with built-in
intervention defaults, and does not require the ADHD-specific threshold config.

``CrisisLevel`` and ``CrisisAssessment`` are defined here (ASFDK's canonical home
for them) and re-exported via ``rrt_advocate``; the foundation adapter imports
them from ``rrt_advocate``.
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import yaml

from crisis.detectors.crisis_detector import CrisisIndicators


class CrisisLevel(Enum):
    """Crisis severity levels."""
    GREEN = "stable"
    YELLOW = "elevated"
    ORANGE = "high"
    RED = "critical"
    BLACK = "emergency"


@dataclass
class CrisisAssessment:
    """Comprehensive crisis assessment."""
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


class CrisisAssessor:
    """
    Maps ``CrisisIndicators`` from the 3-layer CDE to a ``CrisisLevel``.

    Uses aggregate confidence → level thresholds, escalates self-harm signals
    straight to BLACK, and computes a user safety score with penalties for
    looping / behavioral shutdown / sharply declining sentiment. Recommended
    interventions come from the config's ``intervention_mapping`` if present,
    otherwise from domain-neutral built-in defaults.
    """

    # Aggregate confidence → crisis level thresholds.
    _LEVEL_THRESHOLDS = [
        (0.0, 0.20, CrisisLevel.GREEN),
        (0.20, 0.40, CrisisLevel.YELLOW),
        (0.40, 0.70, CrisisLevel.ORANGE),
        (0.70, 0.90, CrisisLevel.RED),
        (0.90, 1.01, CrisisLevel.BLACK),
    ]

    _DEFAULT_INTERVENTIONS: dict[CrisisLevel, list[str]] = {
        CrisisLevel.GREEN: [],
        CrisisLevel.YELLOW: ["breathing_exercise", "grounding_technique"],
        CrisisLevel.ORANGE: ["guided_meditation", "cognitive_restructuring"],
        CrisisLevel.RED: ["intensive_grounding", "crisis_counseling"],
        CrisisLevel.BLACK: ["emergency_stabilization", "crisis_hotline"],
    }

    _ESCALATION_THRESHOLDS: dict[CrisisLevel, float] = {
        CrisisLevel.GREEN: 0.4,
        CrisisLevel.YELLOW: 0.6,
        CrisisLevel.ORANGE: 0.75,
        CrisisLevel.RED: 0.90,
        CrisisLevel.BLACK: 1.0,
    }

    def __init__(self, user_id: str, config_path: str | None = None):
        self.user_id = user_id
        self.logger = logging.getLogger(f"CrisisAssessor-{user_id}")
        self.config = self._load_config(config_path)

    def _load_config(self, path: str | None) -> dict[str, Any]:
        if path and os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as fh:
                    return yaml.safe_load(fh) or {}
            except Exception as exc:  # pragma: no cover - defensive
                self.logger.warning("Failed to load config %s (%s)", path, exc)
        return {}

    async def assess_crisis(self, indicators: CrisisIndicators) -> CrisisAssessment:
        """Produce a CrisisAssessment from aggregated CrisisIndicators."""
        confidence = indicators.aggregate_confidence
        level = self._map_confidence_to_level(confidence)

        # Self-harm always escalates to BLACK regardless of aggregate score.
        if indicators.self_harm_risk:
            level = CrisisLevel.BLACK

        safety_score = self._compute_safety_score(indicators, level)
        interventions = self._get_recommended_interventions(level)

        assessment = CrisisAssessment(
            timestamp=indicators.timestamp,
            crisis_level=level,
            primary_indicators=indicators.get_primary_indicators(),
            secondary_indicators=indicators.detected_semantic_fields,
            confidence_score=round(confidence, 3),
            estimated_duration=None,
            recommended_interventions=interventions,
            escalation_threshold=self._ESCALATION_THRESHOLDS.get(level, 0.8),
            user_safety_score=round(safety_score, 3),
            context_factors={
                "self_harm_risk": indicators.self_harm_risk,
                "sentiment_trend": indicators.sentiment_trend,
                "looping_detected": indicators.looping_detected,
                "behavioral_complexity": indicators.behavioral_complexity,
                "layer_scores": {
                    "keyword": indicators.layer1_confidence,
                    "sentiment": indicators.layer2_confidence,
                    "behavioral": indicators.layer3_confidence,
                },
            },
        )

        self.logger.info(
            "CrisisAssessor: user=%s level=%s confidence=%.2f safety=%.2f",
            self.user_id, level.value, confidence, safety_score,
        )
        return assessment

    def _map_confidence_to_level(self, confidence: float) -> CrisisLevel:
        for low, high, level in self._LEVEL_THRESHOLDS:
            if low <= confidence < high:
                return level
        return CrisisLevel.BLACK

    def _compute_safety_score(
        self, indicators: CrisisIndicators, level: CrisisLevel
    ) -> float:
        """User safety score (1.0 = fully safe, 0.0 = immediate danger).

        Inversely related to aggregate confidence, with extra penalties for
        self-harm, behavioral shutdown, looping, and sharply declining sentiment.
        Self-harm drives the score well below the advocate's 0.3 emergency
        threshold so the pipeline routes to emergency escalation.
        """
        if indicators.self_harm_risk:
            return 0.05

        base = 1.0 - indicators.aggregate_confidence
        if indicators.looping_detected:
            base -= 0.10
        if indicators.behavioral_complexity < 0.10:
            base -= 0.15
        if indicators.sentiment_trend == "sharply_declining":
            base -= 0.10
        return max(0.05, min(1.0, base))

    def _get_recommended_interventions(self, level: CrisisLevel) -> list[str]:
        mapping = self.config.get("intervention_mapping", {})
        level_key = level.name.lower()
        if level_key in mapping:
            return mapping[level_key].get("recommended_interventions", [])
        return list(self._DEFAULT_INTERVENTIONS.get(level, []))
