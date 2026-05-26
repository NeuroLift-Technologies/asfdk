"""Importable package facade for the legacy ``unified-core`` implementation."""

from .neurolift_foundation import (
    FoundationConfig,
    FoundationMode,
    FoundationResponse,
    InteractionType,
    NeuroLiftFoundation,
    UserInteraction,
    create_foundation,
)

__all__ = [
    "FoundationConfig",
    "FoundationMode",
    "FoundationResponse",
    "InteractionType",
    "NeuroLiftFoundation",
    "UserInteraction",
    "create_foundation",
]
