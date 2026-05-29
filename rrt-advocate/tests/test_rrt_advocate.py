"""Tests for the RRT Advocate crisis detection/assessment pipeline.

These exercise the *real* detector and assessor (no mock stand-ins): the
deterministic lexical baseline now produces non-trivial assessments, so we can
assert on actual behavior. Module imports rely on ``rrt-advocate/src`` being on
``sys.path``, which the repo-root ``conftest.py`` arranges.
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


# --- real detection behavior ------------------------------------------------

def test_thresholds_loaded_from_config():
    # The YAML lists suicidal_thoughts at 0.9; confirm it is actually read.
    advocate = _advocate()
    assert advocate.crisis_detector.detection_thresholds["suicidal_thoughts"] == 0.9


def test_benign_message_is_green():
    advocate = _advocate()
    assessment = asyncio.run(advocate.assess_message("Thanks, the report looks great!"))

    assert assessment.crisis_level == CrisisLevel.GREEN
    assert assessment.recommended_interventions == []


def test_empty_input_produces_no_signals():
    advocate = _advocate()
    signals = asyncio.run(advocate.crisis_detector.detect_crisis_indicators())
    assert signals == []
    signals = asyncio.run(advocate.crisis_detector.detect_crisis_indicators({"text": ""}))
    assert signals == []


def test_mild_stress_elevates_but_not_critical():
    advocate = _advocate()
    assessment = asyncio.run(
        advocate.assess_message("I'm feeling really stressed and anxious about this deadline.")
    )

    assert assessment.crisis_level in (CrisisLevel.YELLOW, CrisisLevel.ORANGE)
    assert "stress_level" in (assessment.primary_indicators + assessment.secondary_indicators)
    assert assessment.recommended_interventions  # non-empty advice


def test_suicidal_language_escalates_to_emergency():
    advocate = _advocate()
    assessment = asyncio.run(
        advocate.assess_message("I can't do this anymore, I want to kill myself.")
    )

    # Suicidal ideation is safety-first: never below RED, strong hit -> BLACK.
    assert assessment.crisis_level in (CrisisLevel.RED, CrisisLevel.BLACK)
    assert "suicidal_thoughts" in assessment.primary_indicators
    # Safety score must drop below the advocate's 0.3 emergency threshold.
    assert assessment.user_safety_score < 0.3
    assert "crisis_hotline_988" in assessment.recommended_interventions


def test_assess_message_never_raises_on_bad_input():
    advocate = _advocate()
    # Non-string input should degrade to a safe GREEN default, not raise.
    assessment = asyncio.run(advocate.assess_message(None))  # type: ignore[arg-type]
    assert assessment.crisis_level == CrisisLevel.GREEN
