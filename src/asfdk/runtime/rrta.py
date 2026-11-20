"""Isolated zero-disclosure RRTA support response path."""
from __future__ import annotations

from typing import Any, Dict


class SafeResponseHandler:
    allowed_destinations = ("user:direct_support_stream",)

    def response(self) -> Dict[str, Any]:
        # Deliberately accepts no request, payload, token, or exception data:
        # none can accidentally cross the crisis-stream disclosure boundary.
        return {
            "destination": self.allowed_destinations[0],
            "message": "Support is available. Please reach out to a trusted person or local crisis support now.",
            "zero_disclosure": True,
        }


__all__ = ["SafeResponseHandler"]
