"""Core data types for ASFDK, ported from ``@neurolift-technologies/asfdk``
(``src/types.ts``).

The TypeScript enums become :class:`enum.Enum` subclasses and the TypeScript
interfaces become :func:`dataclasses.dataclass` types. Enum *values* are
preserved verbatim so a mode/interaction string serialized by one
implementation is accepted by the other.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class FoundationMode(str, Enum):
    """Operating modes that determine which Solidarity Framework components are active."""

    #: All components active: TOI-OTOI, Sleepwalker Protocol, and RRT Advocate.
    UNIFIED = "unified"
    #: Crisis routing only: RRT Advocate active, others disabled.
    CRISIS_ONLY = "crisis_only"
    #: Emotional continuity only: Sleepwalker Protocol active, others disabled.
    CONTINUITY_ONLY = "continuity"
    #: TOI governance only: TOI-OTOI validation active, others disabled.
    FRAMEWORK_ONLY = "framework"
    #: Development mode: TOI-OTOI and Sleepwalker active, RRT Advocate disabled.
    DEVELOPMENT = "development"


class InteractionType(str, Enum):
    """Interaction categories that can be routed through the foundation."""

    EMOTIONAL_ASSESSMENT = "emotional_assessment"
    CRISIS_ALERT = "crisis_alert"
    PREFERENCE_UPDATE = "preference_update"
    OPTIMIZATION_REQUEST = "optimization_request"
    STATUS_INQUIRY = "status_inquiry"
    EMERGENCY_ESCALATION = "emergency_escalation"


@dataclass
class FoundationComponents:
    """Per-component activation overrides; defaults are derived from ``mode``."""

    toi_otoi_framework: Optional[bool] = None
    sleepwalker_protocol: Optional[bool] = None
    rrt_advocate: Optional[bool] = None


@dataclass
class FoundationConfig:
    """Configuration for creating a :class:`NeuroLiftFoundation` instance."""

    user_id: str
    mode: FoundationMode
    components: Optional[FoundationComponents] = None


@dataclass
class UserInteraction:
    """A single interaction event submitted to the foundation for processing."""

    timestamp: datetime
    interaction_type: InteractionType
    data: Dict[str, Any]
    user_id: str
    session_id: Optional[str] = None
    priority: Optional[int] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class FoundationResponse:
    """Result returned by :meth:`NeuroLiftFoundation.process_interaction`."""

    timestamp: datetime
    response_type: str
    content: Dict[str, Any]
    #: Names of components that contributed to this response.
    components_involved: List[str]
    success: bool


@dataclass
class ComponentStatus:
    """Live status snapshot for a single Solidarity Framework component."""

    active: bool
    mode: str
    error: Optional[str] = None


@dataclass
class HealthCheckResult:
    """Aggregate health report returned by :meth:`NeuroLiftFoundation.health_check`."""

    healthy: bool
    components: Dict[str, ComponentStatus]
    timestamp: datetime = field(default_factory=datetime.now)


__all__ = [
    "FoundationMode",
    "InteractionType",
    "FoundationComponents",
    "FoundationConfig",
    "UserInteraction",
    "FoundationResponse",
    "ComponentStatus",
    "HealthCheckResult",
]
