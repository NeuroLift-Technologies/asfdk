"""Compatibility wrapper around the legacy ``unified-core`` foundation module."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


_LEGACY_ROOT = Path(__file__).resolve().parent.parent / "unified-core"
_LEGACY_MODULE_PATH = _LEGACY_ROOT / "neurolift_foundation.py"
_LEGACY_MODULE_NAME = "_solidarity_framework_legacy_neurolift_foundation"

if not _LEGACY_MODULE_PATH.exists():
    raise ImportError(f"Legacy foundation module not found at {_LEGACY_MODULE_PATH}")

if str(_LEGACY_ROOT) not in sys.path:
    sys.path.insert(0, str(_LEGACY_ROOT))

_spec = importlib.util.spec_from_file_location(_LEGACY_MODULE_NAME, _LEGACY_MODULE_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load legacy foundation module from {_LEGACY_MODULE_PATH}")

_legacy_module = importlib.util.module_from_spec(_spec)
sys.modules[_LEGACY_MODULE_NAME] = _legacy_module
_spec.loader.exec_module(_legacy_module)

FoundationConfig = _legacy_module.FoundationConfig
FoundationMode = _legacy_module.FoundationMode
FoundationResponse = _legacy_module.FoundationResponse
InteractionType = _legacy_module.InteractionType
NeuroLiftFoundation = _legacy_module.NeuroLiftFoundation
UserInteraction = _legacy_module.UserInteraction
create_foundation = _legacy_module.create_foundation

__all__ = [
    "FoundationConfig",
    "FoundationMode",
    "FoundationResponse",
    "InteractionType",
    "NeuroLiftFoundation",
    "UserInteraction",
    "create_foundation",
]


def __getattr__(name: str):
    return getattr(_legacy_module, name)