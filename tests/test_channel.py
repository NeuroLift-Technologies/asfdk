"""Tests for the Channel enum and normalize_channel function."""
from __future__ import annotations

import pytest

from asfdk.types import Channel, normalize_channel


class TestChannel:
    """Tests for the Channel enum."""

    def test_channel_values(self):
        assert Channel.USER_INPUT.value == "user_input"
        assert Channel.MODEL_OUTPUT.value == "model_output"
        assert Channel.TOOL_RESULT.value == "tool_result"
        assert Channel.SYSTEM.value == "system"
        assert Channel.UNKNOWN.value == "unknown"

    def test_channel_is_string_enum(self):
        assert isinstance(Channel.USER_INPUT, str)
        assert Channel.USER_INPUT == "user_input"


class TestNormalizeChannel:
    """Tests for the normalize_channel function."""

    def test_valid_channel_passes_through(self):
        assert normalize_channel("user_input") == Channel.USER_INPUT
        assert normalize_channel("model_output") == Channel.MODEL_OUTPUT
        assert normalize_channel("tool_result") == Channel.TOOL_RESULT
        assert normalize_channel("system") == Channel.SYSTEM
        assert normalize_channel("unknown") == Channel.UNKNOWN

    def test_invalid_string_collapses_to_unknown(self):
        assert normalize_channel("invalid_channel") == Channel.UNKNOWN

    def test_none_collapses_to_unknown(self):
        assert normalize_channel(None) == Channel.UNKNOWN

    def test_int_collapses_to_unknown(self):
        assert normalize_channel(123) == Channel.UNKNOWN

    def test_dict_collapses_to_unknown(self):
        assert normalize_channel({"channel": "user_input"}) == Channel.UNKNOWN

    def test_empty_string_collapses_to_unknown(self):
        assert normalize_channel("") == Channel.UNKNOWN

    def test_whitespace_collapses_to_unknown(self):
        assert normalize_channel("  user_input  ") == Channel.UNKNOWN

    def test_case_sensitive(self):
        assert normalize_channel("USER_INPUT") == Channel.UNKNOWN
        assert normalize_channel("User_Input") == Channel.UNKNOWN
