"""TOI bootstrap — resolve the ``.toi`` authoring helper the foundation needs.

The canonical authoring helper is ``TOIDocumentGenerator``: privacy-first
defaults, deep-merge of a partial preferences object over those defaults,
``$tier`` handling, and validation against the canonical schema.

It ships in the TypeScript reference (``@neurolift-technologies/toi`` >= 1.0.3).
As of this writing the Python reference (``nlt-toi`` 1.0.0) ships the parser,
canonicalizer, and validator but **not** the generator. Importing
``TOIDocumentGenerator`` from ``nlt_toi`` at module scope therefore made every
``import asfdk`` raise ``ImportError`` — the hard failure published in
``asfdk`` 0.3.0.

This module fixes that without weakening the fail-loud guarantee:

1. Use the pillar's own ``TOIDocumentGenerator`` when it is present (preferred —
   the pillar owns the ``.toi`` standard).
2. Otherwise fall back to :data:`DEFAULT_DOCUMENT`, a verbatim mirror of the
   canonical TypeScript ``DEFAULT_DOCUMENT``, plus the same deep-merge
   semantics.
3. Either way, validate the finished document through the pillar's canonical
   schema (``nlt_toi.parse_toi``) so a document can never be activated unless it
   conforms. Validation failure raises, exactly as before.

:func:`generator_source` reports which path was taken, and the foundation
surfaces it in ``get_system_status()`` so the fallback is never silent.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import nlt_toi

__all__ = [
    "DEFAULT_DOCUMENT",
    "FALLBACK_SOURCE",
    "NATIVE_SOURCE",
    "generator_source",
    "get_generator_class",
    "reset_generator_cache",
]

NATIVE_SOURCE = "nlt_toi"
FALLBACK_SOURCE = "asfdk-fallback"

#: Canonical privacy-first defaults (mirror of ``DEFAULT_DOCUMENT`` in
#: ``@neurolift-technologies/toi`` ``dist/generator.js``). ``identity.author`` is
#: filled in by the generator so a bare merge never yields a conforming document.
DEFAULT_DOCUMENT: Dict[str, Any] = {
    "$toi": nlt_toi.TOI_FORMAT_VERSION,
    "$tier": "personal",
    "identity": {"author": ""},
    "cognitive_profile": {
        "scaffolding_preference": "moderate",
        "attention_model": "variable",
        "energy_model": "variable",
        "thread_support": True,
    },
    "privacy": {
        "retention": "session-only",
        "cross_platform_sharing": "never",
        "training_use": "prohibited",
        "analytics": "prohibited",
        "override_rights": "user-only",
        "data_requests": "honored-immediately",
    },
    "agency": {
        "task_initiation": "user-initiated",
        "ai_suggestions": "on-request",
        "interruptibility": "urgent-only",
        "action_confirmation": "destructive-only",
        "override_authority": "user-final",
    },
    "communication": {
        "tone": "direct",
        "verbosity": "concise",
        "structure": "bullet-points",
        "language": "en",
        "jargon_tolerance": "moderate",
        "pattern_highlighting": False,
        "summary_on_return": True,
        "thread_reconnection": "brief-summary",
    },
    "ethical_pillars": ["user-agency", "privacy-by-default"],
}


def _is_record(value: Any) -> bool:
    """Mirror the TS ``isRecord`` guard: a JSON object, not an array or None."""
    return isinstance(value, dict)


def _deep_merge(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    """Merge ``overlay`` over ``base`` — objects recurse, everything else replaces.

    Mirrors ``deepMerge`` in the canonical generator: lower-precedence defaults
    only fill gaps the caller left unset, and neither input is mutated.
    """
    result = deepcopy(base)
    for key, value in overlay.items():
        base_value = result.get(key)
        if _is_record(value) and _is_record(base_value):
            result[key] = _deep_merge(base_value, value)
        else:
            result[key] = deepcopy(value)
    return result


def _assert_tier(tier: str) -> None:
    """Reject an unknown tier before it can reach the schema validator."""
    if tier not in nlt_toi.TOI_TIERS:
        raise ValueError(
            f"tier must be one of {', '.join(nlt_toi.TOI_TIERS)}; got {tier!r}"
        )


def _today_iso() -> str:
    """UTC date stamp, matching the canonical generator's ``todayIso()``."""
    return datetime.now(timezone.utc).isoformat()[:10]


def _validate(document: Dict[str, Any]) -> Dict[str, Any]:
    """Validate through the pillar's canonical schema; raise on failure.

    ``parse_toi`` is the throwing front door of the ``.toi`` reference
    implementation. Reaching here without it means the installed ``nlt-toi`` is
    older than the ``.toi`` standard itself, which we cannot bootstrap against.
    """
    parse_toi = getattr(nlt_toi, "parse_toi", None)
    if parse_toi is None:  # pragma: no cover - defensive
        raise RuntimeError(
            "the installed nlt-toi does not expose parse_toi(); asfdk requires "
            "nlt-toi>=1.0.0 to validate its active .toi document"
        )
    return parse_toi(document)


class _FallbackGenerator:
    """Local mirror of the canonical ``TOIDocumentGenerator``.

    Used only when the installed ``nlt-toi`` does not export its own generator.
    Defaults, merge semantics, and reserved-key handling mirror
    ``@neurolift-technologies/toi`` ``dist/generator.js``; validation is delegated
    to the pillar's canonical schema, so a fallback-built document is held to the
    same standard as a natively generated one.
    """

    def __init__(self, document: Dict[str, Any]) -> None:
        self.document = document

    @classmethod
    def _build(
        cls,
        preferences: Optional[Dict[str, Any]],
        *,
        author: Optional[str],
        tier: Optional[str],
        handle: Optional[str] = None,
        organization: Optional[str] = None,
    ) -> "_FallbackGenerator":
        document = _deep_merge(DEFAULT_DOCUMENT, preferences or {})

        identity = document.get("identity")
        if not _is_record(identity):
            identity = {}
        document["identity"] = identity
        if author is not None:
            identity["author"] = author
        if not identity.get("author"):
            identity["author"] = "anonymous"
        if handle is not None:
            identity["handle"] = handle
        if organization is not None:
            identity["organization"] = organization

        if tier is None:
            # Preserve a tier supplied inside the preferences object, but never
            # let an unknown one through to the validator.
            _assert_tier(document.get("$tier"))
        else:
            _assert_tier(tier)
            document["$tier"] = tier

        # The merged result is no longer the payload that was signed, so it must
        # not look signed; callers re-sign if they need a signature.
        document.pop("$signature", None)

        return cls(_validate(document))

    @classmethod
    def from_defaults(
        cls,
        author: str = "anonymous",
        tier: Optional[str] = None,
        handle: Optional[str] = None,
        organization: Optional[str] = None,
    ) -> "_FallbackGenerator":
        """Build a privacy-first personal TOI for ``author``."""
        return cls._build(
            None, author=author, tier=tier, handle=handle, organization=organization
        )

    @classmethod
    def from_dict(
        cls,
        preferences: Optional[Dict[str, Any]],
        author: Optional[str] = None,
        tier: Optional[str] = None,
    ) -> "_FallbackGenerator":
        """Build a TOI from a partial preferences object or a full document."""
        return cls._build(preferences, author=author, tier=tier)

    def validate(self) -> "_FallbackGenerator":
        """Re-validate the current document; raises on failure."""
        self.document = _validate(self.document)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Return a fresh copy of the document."""
        return deepcopy(self.document)

    def to_json(self, pretty: bool = True) -> str:
        """Serialize to the on-disk ``.toi`` JSON form."""
        return nlt_toi.serialize_toi(self.document, pretty=pretty)

    def write(self, path: Any, pretty: bool = True) -> None:
        """Write the JSON form of the document to ``path``."""
        from pathlib import Path

        Path(path).write_text(self.to_json(pretty=pretty), encoding="utf-8")


_generator_class: Optional[type] = None


def get_generator_class() -> type:
    """Return the ``.toi`` authoring helper to use.

    Prefers the pillar's own ``TOIDocumentGenerator`` (which owns the standard);
    falls back to :class:`_FallbackGenerator` so that a ``nlt-toi`` release
    without the generator cannot break ``import asfdk``.
    """
    global _generator_class
    if _generator_class is None:
        _generator_class = getattr(nlt_toi, "TOIDocumentGenerator", None) or _FallbackGenerator
    return _generator_class


def generator_source() -> str:
    """Report which authoring helper is in use.

    Returns :data:`NATIVE_SOURCE` when the pillar's generator is available, or
    :data:`FALLBACK_SOURCE` when the local mirror is standing in for it.
    """
    return NATIVE_SOURCE if get_generator_class() is not _FallbackGenerator else FALLBACK_SOURCE


def reset_generator_cache() -> None:
    """Clear the memoized generator lookup (tests / dependency injection)."""
    global _generator_class
    _generator_class = None
