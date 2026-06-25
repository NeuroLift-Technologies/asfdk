"""TOI-OTOI integration adapter, ported from
``@neurolift-technologies/asfdk`` (``src/integration/toi-otoi.ts``).

Wraps the ``nlt_toi`` reference implementation (the single source of truth for
the ``.toi`` v1.0.0 format) and the ``nlt_otoi`` honoring layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from nlt_toi import ToiValidationError, safe_parse_toi
from nlt_otoi import parse_charter


@dataclass
class ValidationIssue:
    """A single validation issue, flattened to a dotted path and a message."""

    message: str
    path: str
    code: str


@dataclass
class TOIValidationResult:
    """Result of a ``.toi`` v1.0.0 schema validation."""

    valid: bool
    errors: Optional[List[ValidationIssue]] = None
    toi: Optional[Dict[str, Any]] = None


def validate_toi(candidate: Any) -> TOIValidationResult:
    """Validate ``candidate`` against the canonical ``.toi`` v1.0.0 schema using
    the ``nlt_toi`` reference implementation. Non-throwing.
    """
    result = safe_parse_toi(candidate)
    if result.success:
        return TOIValidationResult(valid=True, toi=result.data)

    error = result.error
    if isinstance(error, ToiValidationError):
        return TOIValidationResult(
            valid=False,
            errors=[
                ValidationIssue(
                    message=issue.message,
                    path=issue.path,
                    code=error.code,
                )
                for issue in error.issues
            ],
        )
    # ``error`` is not guaranteed to be a ``ToiValidationError`` (a future
    # nlt_toi could surface a different exception). Read ``code`` defensively so
    # the adapter stays non-throwing, mirroring ``validate_charter`` below.
    return TOIValidationResult(
        valid=False,
        errors=[
            ValidationIssue(
                message=str(error), path="", code=getattr(error, "code", "error")
            )
        ],
    )


@dataclass
class OTOIValidationResult:
    """Result of an ``.otoi`` charter validation."""

    valid: bool
    errors: Optional[List[ValidationIssue]] = None
    charter: Optional[Any] = None


def validate_charter(candidate: Any) -> OTOIValidationResult:
    """Validate ``candidate`` against the ``.otoi`` charter schema using the
    ``nlt_otoi`` honoring layer. A ``.otoi`` charter declares how a mesh of
    agents honors a stack of ``.toi`` documents at runtime.
    """
    try:
        charter = parse_charter(candidate)
        return OTOIValidationResult(valid=True, charter=charter)
    except Exception as err:  # noqa: BLE001 - mirror TS catch-all boundary
        message = str(err)
        code = getattr(err, "code", None) or "error"
        return OTOIValidationResult(
            valid=False,
            errors=[ValidationIssue(message=message, path="", code=code)],
        )


def get_status() -> Dict[str, Any]:
    """Return the active TOI-OTOI component status."""
    return {"active": True, "mode": "toi-otoi-validation"}


__all__ = [
    "ValidationIssue",
    "TOIValidationResult",
    "validate_toi",
    "OTOIValidationResult",
    "validate_charter",
    "get_status",
]
