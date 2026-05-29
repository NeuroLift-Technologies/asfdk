"""Tests for the RRT Advocate crisis detection/assessment pipeline.

These exercise the real 3-layer CDE pipeline (keyword + sentiment + behavioral)
ported from the canonical NeuroLift-Technologies/rrt-advocate. Module imports
rely on ``rrt-advocate/src`` being on ``sys.path``, which the repo-root
``conftest.py`` arranges.
"""

import asyncio
import os

from rrt_advocate import CrisisLevel, RRTAdvocate

_CONFIG = os.path.join(
    os.path.dirname(__file__), os.pardir, "config", "crisis_thresholds.yaml"
)


def _advocate(user_id="user-1"):
    return RRTAdvocate(user_id=user_id, config_path=_CONFIG)


# --- structural / safe-default behavior ------------------------------------

def test_get_status_report_has_expected_shape():
    advocate = _advocate("user-1")
    status = asyncio.run(advocate.get_status_report())

    assert status["user_id"] == "user-1"
    assert status["monitoring_active"] is False
    assert status["current_crisis"]["level"] == "none"
    assert status["performance"]["avg_response_time"] == 0.0


def test_assess_current_state_returns_safe_default_on_detector_failure():
    advocate = _advocate("user-2")

    async def broken_detector(*_args, **_kwargs):
        raise RuntimeError("detector unavailable")

    advocate.crisis_detector.detect_crisis_indicators = broken_detector
    assessment = asyncio.run(advocate.assess_current_state())

    assert assessment.crisis_level == CrisisLevel.GREEN
    assert assessment.user_safety_score == 1.0
    assert assessment.confidence_score == 0.0


def test_manual_intervention_deploys_and_tracks():
    advocate = _advocate("user-3")
    ok = asyncio.run(advocate.manual_intervention("grounding"))

    # The intervention manager returns an active response, so the advocate
    # reports success and tracks it as an active intervention.
    assert ok is True
    assert len(advocate.active_interventions) == 1


# --- real 3-layer detection behavior ---------------------------------------

def test_benign_message_is_green():
    advocate = _advocate()
    assessment = asyncio.run(advocate.assess_message("Thanks, the report looks great!"))

    assert assessment.crisis_level == CrisisLevel.GREEN
    assert assessment.recommended_interventions == []
    assert assessment.context_factors["self_harm_risk"] is False


def test_empty_message_is_green():
    advocate = _advocate()
    assessment = asyncio.run(advocate.assess_message(""))
    assert assessment.crisis_level == CrisisLevel.GREEN
    assert assessment.confidence_score == 0.0


def test_distress_language_elevates_but_not_critical():
    advocate = _advocate()
    assessment = asyncio.run(
        advocate.assess_message(
            "I'm worthless and I can't cope. Everything is too much and I'm falling apart."
        )
    )

    assert assessment.crisis_level in (CrisisLevel.YELLOW, CrisisLevel.ORANGE)
    # Keyword layer should have flagged overwhelm and/or negative self-talk.
    detected = assessment.secondary_indicators
    assert any(f in detected for f in ("overwhelm", "negative_self_talk"))
    assert assessment.context_factors["self_harm_risk"] is False
    assert assessment.recommended_interventions  # non-empty advice


def test_self_harm_language_escalates_to_emergency():
    advocate = _advocate()
    assessment = asyncio.run(
        advocate.assess_message("I can't do this anymore, I want to kill myself.")
    )

    # Self-harm is safety-first: always BLACK, regardless of other signals.
    assert assessment.crisis_level == CrisisLevel.BLACK
    assert assessment.context_factors["self_harm_risk"] is True
    assert "SELF_HARM_RISK" in assessment.primary_indicators
    # Safety score must drop below the advocate's 0.3 emergency threshold.
    assert assessment.user_safety_score < 0.3
    assert "crisis_hotline" in assessment.recommended_interventions


def test_assess_message_never_raises_on_bad_input():
    advocate = _advocate()
    # Non-string input should degrade to a safe GREEN default, not raise.
    assessment = asyncio.run(advocate.assess_message(None))  # type: ignore[arg-type]
    assert assessment.crisis_level == CrisisLevel.GREEN
