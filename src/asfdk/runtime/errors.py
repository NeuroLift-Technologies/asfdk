"""Fail-closed ADR-001 runtime errors."""
from __future__ import annotations

from typing import Any, Dict, Optional


class PolicyDenied(PermissionError):
    """A deterministic policy denial with a stable machine-readable code."""

    def __init__(self, code: str, message: str, *, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def as_dict(self) -> Dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


__all__ = ["PolicyDenied"]
