"""
Crisis Detector - Detects crisis indicators from various data sources

SAFETY NOTE
-----------
This module ships a *deterministic, lexical baseline* detector. It scans text
for configurable indicator phrases and emits ``CrisisSignal`` objects. It is:

  * transparent and auditable (no opaque model, no network call),
  * provider-agnostic (it does NOT pick or require any LLM — see the
    no-LLM-lock-in guardrail in AGENTS.md / OTOI Section 4.4), and
  * intended as a safe default that adopters extend or replace.

It is **not** a clinical instrument and will miss indirect or coded language
(false negatives are expected). Adopters who need higher recall should provide
a richer detector (for example a model-backed one, such as the Cloudflare
Worker implementation in ``workers/src/rrt-advocate.ts``) by subclassing
``CrisisDetector`` and overriding :meth:`detect_crisis_indicators`. The rest of
the RRT Advocate pipeline depends only on the ``CrisisSignal`` contract, so any
detector that returns ``CrisisSignal`` objects will work unchanged.
"""

import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - pyyaml is a declared core dependency
    yaml = None


class CrisisIndicator(Enum):
    """Types of crisis indicators"""
    STRESS_LEVEL = "stress_level"
    PANIC_SYMPTOMS = "panic_symptoms"
    OVERWHELM = "overwhelm"
    ISOLATION = "isolation"
    SUICIDAL_THOUGHTS = "suicidal_thoughts"
    SUBSTANCE_ABUSE = "substance_abuse"
    SLEEP_DISTURBANCE = "sleep_disturbance"
    APPETITE_CHANGE = "appetite_change"


@dataclass
class CrisisSignal:
    """Individual crisis signal"""
    indicator: CrisisIndicator
    intensity: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    source: str
    context: dict[str, Any] = field(default_factory=dict)


# Default thresholds, used only when the config file cannot be read. These
# mirror the ``support_thresholds`` block of config/crisis_thresholds.yaml.
_DEFAULT_THRESHOLDS: dict[str, float] = {
    "stress_level": 0.7,
    "panic_symptoms": 0.8,
    "overwhelm": 0.6,
    "isolation": 0.5,
    "suicidal_thoughts": 0.9,
    "substance_abuse": 0.7,
    "sleep_disturbance": 0.6,
    "appetite_change": 0.5,
}

# Deterministic phrase lexicon. Each indicator maps to (regex pattern, weight)
# pairs. Weight is the strength of a single match (0.0-1.0); when several
# patterns for one indicator match, intensity is the strongest weight plus a
# small per-extra-match bonus (see detect_crisis_indicators). Patterns are
# matched case-insensitively on word boundaries. This table is intentionally
# simple and reviewable; it is the single place to tune lexical recall without
# touching pipeline logic.
_LEXICON: dict[CrisisIndicator, list[tuple]] = {
    CrisisIndicator.SUICIDAL_THOUGHTS: [
        (r"\bkill myself\b", 1.0),
        (r"\bend my life\b", 1.0),
        (r"\bsuicid(e|al)\b", 1.0),
        (r"\bdon'?t want to (be alive|live)\b", 0.95),
        (r"\bbetter off (dead|without me)\b", 0.9),
        (r"\bwant to die\b", 0.95),
        (r"\bno reason to (live|go on)\b", 0.85),
    ],
    CrisisIndicator.PANIC_SYMPTOMS: [
        (r"\bpanic attack\b", 0.9),
        (r"\bcan'?t breathe\b", 0.8),
        (r"\bheart (is )?racing\b", 0.6),
        (r"\bhyperventilat", 0.7),
    ],
    CrisisIndicator.SUBSTANCE_ABUSE: [
        (r"\brelaps(e|ed|ing)\b", 0.8),
        (r"\bcan'?t stop (drinking|using)\b", 0.8),
        (r"\boverdos", 0.9),
        (r"\bdrinking too much\b", 0.6),
    ],
    CrisisIndicator.OVERWHELM: [
        (r"\boverwhelmed\b", 0.6),
        (r"\bcan'?t cope\b", 0.7),
        (r"\btoo much (to handle|for me)\b", 0.6),
        (r"\bfalling apart\b", 0.7),
        (r"\bbreaking down\b", 0.65),
    ],
    CrisisIndicator.STRESS_LEVEL: [
        (r"\bstressed( out)?\b", 0.5),
        (r"\banxious\b", 0.5),
        (r"\banxiety\b", 0.5),
        (r"\bburn(ed|t) out\b", 0.6),
        (r"\bso much pressure\b", 0.5),
    ],
    CrisisIndicator.ISOLATION: [
        (r"\ball alone\b", 0.6),
        (r"\bno one (cares|would notice)\b", 0.7),
        (r"\bnobody (cares|understands)\b", 0.6),
        (r"\bso lonely\b", 0.55),
        (r"\bcompletely isolated\b", 0.6),
    ],
    CrisisIndicator.SLEEP_DISTURBANCE: [
        (r"\bcan'?t sleep\b", 0.5),
        (r"\bhaven'?t slept\b", 0.55),
        (r"\binsomnia\b", 0.5),
        (r"\bnightmares\b", 0.45),
    ],
    CrisisIndicator.APPETITE_CHANGE: [
        (r"\bnot eating\b", 0.5),
        (r"\bhaven'?t eaten\b", 0.5),
        (r"\bno appetite\b", 0.45),
        (r"\bcan'?t keep food down\b", 0.5),
    ],
}


class CrisisDetector:
    """Detects crisis indicators from various data sources."""

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.logger = logging.getLogger("CrisisDetector")
        self.detection_thresholds = self._load_thresholds()
        # Precompile patterns once for efficiency.
        self._compiled: dict[CrisisIndicator, list[tuple]] = {
            indicator: [(re.compile(pat, re.IGNORECASE), weight) for pat, weight in entries]
            for indicator, entries in _LEXICON.items()
        }

    def _load_thresholds(self) -> dict[str, float]:
        """Load crisis detection thresholds from the YAML config.

        Reads the ``support_thresholds`` block of ``crisis_thresholds.yaml``.
        Falls back to built-in defaults if the file is missing/unreadable so
        the detector never fails closed in a way that silences detection.
        """
        if yaml is not None and self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, encoding="utf-8") as fh:
                    data = yaml.safe_load(fh) or {}
                thresholds = data.get("support_thresholds", {})
                merged = dict(_DEFAULT_THRESHOLDS)
                # Only copy numeric scalar thresholds (skip nested dicts like
                # ``custom_indicators``) and only those we model as indicators.
                for key, value in thresholds.items():
                    if isinstance(value, (int, float)):
                        merged[key] = float(value)
                return merged
            except Exception as exc:  # pragma: no cover - defensive
                self.logger.warning(
                    "Failed to load thresholds from %s (%s); using defaults",
                    self.config_path, exc,
                )
        return dict(_DEFAULT_THRESHOLDS)

    async def detect_crisis_indicators(
        self, context: dict[str, Any] | None = None
    ) -> list[CrisisSignal]:
        """Detect crisis indicators from available data sources.

        Args:
            context: Optional data to analyze. Recognized keys:
                * ``"text"`` (str): a single message/utterance to scan.
                * ``"messages"`` (list[dict|str]): recent turns; dicts may carry
                  ``{"content": ...}``. All text is concatenated and scanned.
                When ``context`` is ``None`` or carries no text, an empty list
                is returned — i.e. the detector never fabricates signals from
                no input (no false positives on an empty buffer).

        Returns:
            A list of ``CrisisSignal`` objects, one per indicator that matched.
        """
        text = self._extract_text(context)
        if not text:
            return []

        now = datetime.now()
        source = (context or {}).get("source", "text_input")
        signals: list[CrisisSignal] = []

        for indicator, entries in self._compiled.items():
            matched_terms: list[str] = []
            matched_weights: list[float] = []
            for pattern, weight in entries:
                if pattern.search(text):
                    matched_weights.append(weight)
                    matched_terms.append(pattern.pattern)
            if matched_terms:
                # Intensity is the strongest single match plus a small bonus per
                # corroborating match — so several *mild* hits stay moderate
                # rather than summing straight to the ceiling.
                intensity = min(max(matched_weights) + 0.1 * (len(matched_weights) - 1), 1.0)
                # Confidence grows with the number of corroborating matches but
                # stays bounded; a single lexical hit is suggestive, not certain.
                confidence = min(0.5 + 0.25 * (len(matched_terms) - 1), 0.95)
                signals.append(
                    CrisisSignal(
                        indicator=indicator,
                        intensity=intensity,
                        confidence=confidence,
                        timestamp=now,
                        source=source,
                        context={"matched_terms": matched_terms},
                    )
                )

        return signals

    @staticmethod
    def _extract_text(context: dict[str, Any] | None) -> str:
        """Flatten recognized context fields into a single searchable string."""
        if not context:
            return ""
        parts: list[str] = []
        text = context.get("text")
        if isinstance(text, str):
            parts.append(text)
        messages = context.get("messages")
        if isinstance(messages, list):
            for msg in messages:
                if isinstance(msg, str):
                    parts.append(msg)
                elif isinstance(msg, dict) and isinstance(msg.get("content"), str):
                    parts.append(msg["content"])
        return "\n".join(parts).strip()
