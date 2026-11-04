"""RRT runs on every EMOTIONAL_ASSESSMENT when it is active.

Background: Sleepwalker's detector does not flag every statement RRT recognizes
("I want to die" returns emergency from RRT alone), and RRT used to be called
only when Sleepwalker asked for a handoff. Mirrors the TypeScript tests in
``packages/asfdk/tests/index.test.ts``.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from asfdk import FoundationConfig, FoundationMode, NeuroLiftFoundation
from asfdk.integration import rrt, sleepwalker
from asfdk.types import Channel, InteractionType, UserInteraction


def _foundation(mode: FoundationMode, user: str) -> NeuroLiftFoundation:
    return NeuroLiftFoundation(FoundationConfig(user_id=user, mode=mode))


async def _assess(f: NeuroLiftFoundation, user: str, text: str, channel: Channel):
    return await f.process_interaction(
        UserInteraction(
            timestamp=datetime.now(timezone.utc),
            interaction_type=InteractionType.EMOTIONAL_ASSESSMENT,
            data={"text": text},
            user_id=user,
            channel=channel,
        )
    )


async def test_unified_assesses_a_statement_rrt_recognizes_even_if_sleepwalker_does_not_flag_it():
    f = _foundation(FoundationMode.UNIFIED, "r1")
    response = await _assess(f, "r1", "I want to die", Channel.USER_INPUT)
    assert response.components_involved == ["rrt_advocate", "sleepwalker_protocol"]
    assert response.content["rrt"].crisis_level == rrt.CrisisLevel.BLACK


async def test_unified_rrt_high_reading_raises_the_gate_on_an_untrusted_channel():
    f = _foundation(FoundationMode.UNIFIED, "r2")
    untrusted = await _assess(f, "r2", "I want to die", Channel.UNKNOWN)
    assert untrusted.content["trusted"] is False
    assert untrusted.content["gateUp"] is True
    trusted = await _assess(f, "r2", "I want to die", Channel.USER_INPUT)
    assert trusted.content["gateUp"] is False


async def test_unified_benign_text_is_assessed_reads_stable_and_does_not_raise_the_gate():
    f = _foundation(FoundationMode.UNIFIED, "r3")
    response = await _assess(f, "r3", "Add a unit test for the parser.", Channel.UNKNOWN)
    assert "rrt_advocate" in response.components_involved
    assert response.content["rrt"].crisis_level == rrt.CrisisLevel.GREEN
    assert response.content["gateUp"] is False


async def test_crisis_only_emotional_assessments_are_routed_to_rrt():
    f = _foundation(FoundationMode.CRISIS_ONLY, "r4")
    response = await _assess(f, "r4", "I want to kill myself", Channel.UNKNOWN)
    assert response.components_involved == ["rrt_advocate"]
    assert "emotionalState" not in response.content
    assert response.content["rrt"].crisis_level == rrt.CrisisLevel.BLACK
    assert response.content["gateUp"] is True


async def test_continuity_only_and_framework_only_are_unchanged():
    continuity = await _assess(
        _foundation(FoundationMode.CONTINUITY_ONLY, "r5"), "r5", "I want to die", Channel.USER_INPUT
    )
    assert continuity.components_involved == ["sleepwalker_protocol"]
    assert "rrt" not in continuity.content

    framework = await _assess(
        _foundation(FoundationMode.FRAMEWORK_ONLY, "r6"), "r6", "I want to die", Channel.USER_INPUT
    )
    assert framework.components_involved == []


async def test_rrt_failure_is_attributed_to_rrt_and_keeps_the_sleepwalker_result(monkeypatch):
    async def boom(*_args, **_kwargs):
        raise RuntimeError("rrt boom")

    monkeypatch.setattr(rrt, "assess", boom)
    f = _foundation(FoundationMode.UNIFIED, "r7")
    response = await _assess(f, "r7", "I feel overwhelmed today", Channel.USER_INPUT)
    assert response.success is True
    assert "emotionalState" in response.content
    assert response.content["error"]["component"] == "rrt_advocate"
    assert response.components_involved == ["rrt_advocate", "sleepwalker_protocol"]


async def test_sleepwalker_failure_no_longer_skips_rrt(monkeypatch):
    def boom(*_args, **_kwargs):
        raise RuntimeError("swp boom")

    monkeypatch.setattr(sleepwalker, "detect_emotional_state", boom)
    f = _foundation(FoundationMode.UNIFIED, "r8")
    response = await _assess(f, "r8", "I want to die", Channel.UNKNOWN)
    assert response.components_involved == ["rrt_advocate", "sleepwalker_protocol"]
    assert response.content["rrt"].crisis_level == rrt.CrisisLevel.BLACK
    assert response.content["gateUp"] is True
