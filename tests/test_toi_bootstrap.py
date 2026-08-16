"""TOI bootstrap: the generator runs before any component activates.

Run from the repo root with the pillar packages on ``PYTHONPATH``, e.g.::

    PYTHONPATH=src:../nlt-otoi/src:../rrt-advocate/src:../sleepwalker/src \
        python3 -m pytest tests/test_toi_bootstrap.py -q

These tests use ``asyncio.run`` directly so they do not require pytest-asyncio.
"""
from __future__ import annotations

import asyncio
import json
import tempfile

from asfdk import FoundationConfig, FoundationMode, NeuroLiftFoundation, create_foundation


def _run(coro):
    return asyncio.run(coro)


def test_default_source_generates_personal_toi():
    foundation = _run(create_foundation("user-1", FoundationMode.UNIFIED))
    doc = foundation.get_active_toi()
    assert doc is not None
    assert doc["$tier"] == "personal"
    assert doc["$toi"] == "1.0.0"
    assert doc["identity"]["author"] == "anonymous"
    assert foundation.get_system_status()["toi"]["generated"] is True


def test_dict_source_merges_over_defaults():
    foundation = _run(
        create_foundation(
            FoundationConfig(
                user_id="u2",
                mode=FoundationMode.UNIFIED,
                toi={"communication": {"tone": "friendly"}},
            )
        )
    )
    doc = foundation.get_active_toi()
    assert doc["communication"]["tone"] == "friendly"
    # Untouched defaults survive the merge.
    assert doc["privacy"]["retention"] == "session-only"


def test_file_source_is_parsed_and_regenerated():
    with tempfile.NamedTemporaryFile("w", suffix=".toi", delete=False) as handle:
        json.dump({"$toi": "1.0.0", "$tier": "project", "identity": {"author": "carol"}}, handle)
        path = handle.name
    try:
        foundation = _run(
            create_foundation(
                FoundationConfig(user_id="u3", mode=FoundationMode.UNIFIED, toi=path)
            )
        )
        doc = foundation.get_active_toi()
        assert doc["$tier"] == "project"
        assert doc["identity"]["author"] == "carol"
    finally:
        import os

        os.unlink(path)


def test_invalid_source_raises_before_activation():
    foundation = NeuroLiftFoundation(
        FoundationConfig(
            user_id="u4",
            mode=FoundationMode.UNIFIED,
            toi={"communication": {"tone": "gibberish"}},
        )
    )
    try:
        _run(foundation.initialize())
        assert False, "initialize() should raise on an invalid TOI source"
    except Exception:
        pass
    # Fail-loud: nothing activates, and the TOI is not set.
    assert foundation.get_active_toi() is None
    assert foundation.get_system_status()["initialized"] is False


def test_initialize_is_idempotent_via_start():
    foundation = _run(create_foundation("user-5", FoundationMode.FRAMEWORK_ONLY))
    _run(foundation.start())
    assert foundation.get_active_toi() is not None