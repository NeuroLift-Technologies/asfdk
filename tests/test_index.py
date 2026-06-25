"""Conformance test suite for ``asfdk``, ported verbatim (in behavior) from
``@neurolift-technologies/asfdk``'s ``tests/index.test.ts``.

Every assertion mirrors a TypeScript ``it(...)`` block. The cross-implementation
gate is that these behavioral tests pass against the *real* Python pillar ports
(``nlt_toi``, ``nlt_otoi``, ``rrt_advocate``, ``sleepwalker_protocol``) — the same
way the npm suite runs against the npm pillars.
"""
from __future__ import annotations

from datetime import datetime

import pytest

from asfdk import (
    FoundationMode,
    InteractionType,
    NeuroLiftFoundation,
    create_foundation,
    otoi,
    rrt,
    sleepwalker,
    toi,
)
from asfdk.types import FoundationConfig, UserInteraction


# --- createFoundation ---------------------------------------------------------
class TestCreateFoundation:
    @pytest.mark.asyncio
    async def test_resolves_with_a_neurolift_foundation_instance(self):
        f = await create_foundation("test-user", FoundationMode.FRAMEWORK_ONLY)
        assert isinstance(f, NeuroLiftFoundation)

    @pytest.mark.asyncio
    async def test_accepts_a_foundation_config_object(self):
        f = await create_foundation(
            FoundationConfig(user_id="test-user", mode=FoundationMode.DEVELOPMENT)
        )
        assert isinstance(f, NeuroLiftFoundation)


# --- NeuroLiftFoundation.healthCheck ------------------------------------------
class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_returns_a_well_formed_health_result(self):
        f = await create_foundation("u1", FoundationMode.UNIFIED)
        result = await f.health_check()
        assert result.healthy is True
        assert isinstance(result.timestamp, datetime)
        assert "toi_otoi_framework" in result.components
        assert "sleepwalker_protocol" in result.components
        assert "rrt_advocate" in result.components

    @pytest.mark.asyncio
    async def test_framework_only_toi_active_swp_disabled(self):
        f = await create_foundation("u1", FoundationMode.FRAMEWORK_ONLY)
        result = await f.health_check()
        assert result.components["toi_otoi_framework"].active is True
        assert result.components["sleepwalker_protocol"].active is False

    @pytest.mark.asyncio
    async def test_continuity_only_swp_active_toi_disabled(self):
        f = await create_foundation("u1", FoundationMode.CONTINUITY_ONLY)
        result = await f.health_check()
        assert result.components["toi_otoi_framework"].active is False
        assert result.components["sleepwalker_protocol"].active is True

    @pytest.mark.asyncio
    async def test_rrt_active_with_crisis_detection_in_unified(self):
        f = await create_foundation("u1", FoundationMode.UNIFIED)
        result = await f.health_check()
        assert result.components["rrt_advocate"].active is True
        assert result.components["rrt_advocate"].mode == "crisis-detection"

    @pytest.mark.asyncio
    async def test_rrt_disabled_in_framework_only(self):
        f = await create_foundation("u1", FoundationMode.FRAMEWORK_ONLY)
        result = await f.health_check()
        assert result.components["rrt_advocate"].active is False
        assert result.components["rrt_advocate"].mode == "disabled"


# --- NeuroLiftFoundation.getSystemStatus --------------------------------------
class TestGetSystemStatus:
    @pytest.mark.asyncio
    async def test_returns_the_mode_and_user_id(self):
        f = await create_foundation("joshua", FoundationMode.CRISIS_ONLY)
        status = f.get_system_status()
        assert status["mode"] == FoundationMode.CRISIS_ONLY
        assert status["userId"] == "joshua"
        assert status["initialized"] is True

    @pytest.mark.asyncio
    async def test_disabled_components_include_mode_disabled(self):
        f = await create_foundation("u1", FoundationMode.CRISIS_ONLY)
        status = f.get_system_status()
        assert status["components"]["toi_otoi_framework"]["mode"] == "disabled"
        assert status["components"]["sleepwalker_protocol"]["mode"] == "disabled"


# --- NeuroLiftFoundation.processInteraction -----------------------------------
class TestProcessInteraction:
    @pytest.mark.asyncio
    async def test_emotional_assessment_returns_emotional_state_continuity_only(self):
        f = await create_foundation("u1", FoundationMode.CONTINUITY_ONLY)
        response = await f.process_interaction(
            UserInteraction(
                timestamp=datetime.now(),
                interaction_type=InteractionType.EMOTIONAL_ASSESSMENT,
                data={"text": "I feel overwhelmed today"},
                user_id="u1",
            )
        )
        assert response.success is True
        assert "sleepwalker_protocol" in response.components_involved
        assert "emotionalState" in response.content

    @pytest.mark.asyncio
    async def test_preference_update_with_invalid_toi_raises_framework_only(self):
        f = await create_foundation("u1", FoundationMode.FRAMEWORK_ONLY)
        with pytest.raises(ValueError, match="TOI validation failed"):
            await f.update_preferences({"notAToi": True})

    @pytest.mark.asyncio
    async def test_crisis_alert_routes_to_rrt_advocate_crisis_only(self):
        f = await create_foundation("u1", FoundationMode.CRISIS_ONLY)
        response = await f.process_interaction(
            UserInteraction(
                timestamp=datetime.now(),
                interaction_type=InteractionType.CRISIS_ALERT,
                data={"text": "I need help now"},
                user_id="u1",
            )
        )
        assert response.success is True
        assert "rrt_advocate" in response.components_involved
        assert "rrt" in response.content

    @pytest.mark.asyncio
    async def test_unknown_interaction_type_returns_empty_components(self):
        f = await create_foundation("u1", FoundationMode.UNIFIED)
        response = await f.process_interaction(
            UserInteraction(
                timestamp=datetime.now(),
                interaction_type=InteractionType.STATUS_INQUIRY,
                data={},
                user_id="u1",
            )
        )
        assert response.success is True
        assert len(response.components_involved) == 0


# --- NeuroLiftFoundation.assessEmotionalState ---------------------------------
class TestAssessEmotionalState:
    @pytest.mark.asyncio
    async def test_returns_an_assessment_when_sleepwalker_active(self):
        f = await create_foundation("u1", FoundationMode.CONTINUITY_ONLY)
        result = await f.assess_emotional_state("I am feeling overwhelmed")
        assert result is not None

    @pytest.mark.asyncio
    async def test_returns_none_when_sleepwalker_not_active(self):
        f = await create_foundation("u1", FoundationMode.FRAMEWORK_ONLY)
        result = await f.assess_emotional_state("I am feeling overwhelmed")
        assert result is None


# --- NeuroLiftFoundation.updatePreferences ------------------------------------
class TestUpdatePreferences:
    @pytest.mark.asyncio
    async def test_resolves_without_error_for_valid_toi_document(self):
        f = await create_foundation("u1", FoundationMode.FRAMEWORK_ONLY)
        result = await f.update_preferences(
            {"$toi": "1.0.0", "$tier": "personal", "identity": {"author": "test-user"}}
        )
        assert result is None


# --- NeuroLiftFoundation.shutdown ---------------------------------------------
class TestShutdown:
    @pytest.mark.asyncio
    async def test_marks_the_foundation_as_uninitialized(self):
        f = await create_foundation("u1", FoundationMode.DEVELOPMENT)
        assert f.get_system_status()["initialized"] is True
        await f.shutdown()
        assert f.get_system_status()["initialized"] is False


# --- pillar umbrella re-exports -----------------------------------------------
class TestPillarUmbrellaReExports:
    @pytest.mark.asyncio
    async def test_surfaces_the_four_solidarity_framework_pillar_packages(self):
        # nlt_toi
        good = toi.safe_parse_toi(
            {"$toi": "1.0.0", "$tier": "personal", "identity": {"author": "u1"}}
        )
        assert good.success is True
        assert callable(toi.parse_toi)

        # nlt_otoi
        assert callable(otoi.honor)
        assert callable(otoi.propagate)

        # rrt_advocate
        assert callable(rrt.CrisisEngine)
        assessment = rrt.CrisisEngine("u1").assess("just checking in, doing fine")
        assert hasattr(assessment, "crisis_level")

        # sleepwalker_protocol
        assert callable(sleepwalker.SleepwalkerProtocol)
