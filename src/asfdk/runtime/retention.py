"""Consent-scoped telemetry with fail-closed PASSIVE anonymization."""
from __future__ import annotations

import json
import re
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from cryptography.fernet import Fernet, InvalidToken

from .crypto import canonical_json
from .errors import PolicyDenied
from .models import Consent


class PassiveAnonymizer:
    """Two stages: PII redaction, then distinct-user 24-hour cohort validation."""

    _patterns = (
        re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
        re.compile(r"(?<!\d)(?:\+?\d[ .-]?){8,14}\d(?!\d)"),
        re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    )

    def scrub(self, value: Any) -> Any:
        if isinstance(value, str):
            for pattern in self._patterns:
                value = pattern.sub("[REDACTED]", value)
            return value
        if isinstance(value, dict):
            return {str(key): self.scrub(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [self.scrub(item) for item in value]
        return value


class AuditLedger:
    def __init__(self, consent: Consent, *, storage_path: Optional[str] = None,
                 local_single_user: bool = True, encryption_key: Optional[bytes] = None,
                 minimum_cohort: int = 10) -> None:
        self.consent = consent
        self.local_single_user = local_single_user
        self.minimum_cohort = max(10, minimum_cohort)
        self._anonymizer = PassiveAnonymizer()
        self._pending: Dict[str, Dict[str, float]] = {}
        self._memory_records: List[Dict[str, Any]] = []
        self._storage_path = storage_path
        self._fernet = None
        if consent in (Consent.ACTIVE, Consent.EXPLICIT):
            if not encryption_key:
                raise PolicyDenied("AUDIT_ENCRYPTION_REQUIRED", "Full-trace audit encryption key is required")
            try:
                self._fernet = Fernet(encryption_key)
            except (TypeError, ValueError) as err:
                raise PolicyDenied("AUDIT_ENCRYPTION_REQUIRED", "Invalid audit encryption key") from err
        if storage_path and consent != Consent.NONE:
            Path(storage_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
            with self._connect() as connection:
                connection.execute(
                    "CREATE TABLE IF NOT EXISTS audit_ledger "
                    "(id INTEGER PRIMARY KEY AUTOINCREMENT, created REAL NOT NULL, payload TEXT NOT NULL)"
                )

    @property
    def cipher(self) -> Any:
        return self._fernet

    def _connect(self) -> sqlite3.Connection:
        if not self._storage_path:
            raise RuntimeError("audit storage is not configured")
        return sqlite3.connect(self._storage_path, timeout=5)

    def record(self, event_type: str, details: Dict[str, Any], *, user_id: str,
               now: Optional[float] = None) -> bool:
        timestamp = time.time() if now is None else now
        if self.consent == Consent.NONE:
            return False
        if self.consent == Consent.PASSIVE:
            if self.local_single_user:
                self._pending.clear()
                raise PolicyDenied(
                    "DENY_UNVERIFIED_ANONYMIZATION",
                    "PASSIVE telemetry is auto-drop on a local single-user setup",
                )
            self._anonymizer.scrub(details)
            cohort = self._pending.setdefault(event_type, {})
            cohort[user_id] = timestamp
            cutoff = timestamp - 24 * 60 * 60
            self._pending = {
                key: {user: seen for user, seen in users.items() if seen >= cutoff}
                for key, users in self._pending.items()
            }
            cohort = self._pending.get(event_type, {})
            if len(cohort) < self.minimum_cohort:
                return False
            payload = {
                "event_type": event_type,
                "cohort_size": len(cohort), "window_hours": 24,
            }
            self._persist(payload, timestamp, encrypted=False)
            return True

        self._persist({"event_type": event_type, "details": details}, timestamp, encrypted=True)
        return True

    def _persist(self, payload: Dict[str, Any], timestamp: float, *, encrypted: bool) -> None:
        serialized = canonical_json(payload)
        stored = self._fernet.encrypt(serialized).decode("ascii") if encrypted else serialized.decode("utf-8")
        if self._storage_path:
            with self._connect() as connection:
                connection.execute("INSERT INTO audit_ledger (created, payload) VALUES (?, ?)",
                                   (timestamp, stored))
        else:
            self._memory_records.append({"created": timestamp, "payload": stored})

    def records(self) -> List[Dict[str, Any]]:
        rows = list(self._memory_records)
        if self._storage_path and self.consent != Consent.NONE:
            with self._connect() as connection:
                rows.extend({"created": row[0], "payload": row[1]} for row in connection.execute(
                    "SELECT created, payload FROM audit_ledger ORDER BY id"
                ))
        result = []
        for row in rows:
            try:
                raw = self._fernet.decrypt(row["payload"].encode("ascii")) if self._fernet else row["payload"].encode()
                result.append(json.loads(raw))
            except (InvalidToken, ValueError) as err:
                raise PolicyDenied("AUDIT_INTEGRITY_ERROR", "Audit record cannot be verified") from err
        return result

    def update_consent(self, consent: Consent) -> None:
        downgraded = list(Consent).index(consent) < list(Consent).index(self.consent)
        if consent in (Consent.ACTIVE, Consent.EXPLICIT) and self._fernet is None:
            raise PolicyDenied(
                "AUDIT_ENCRYPTION_REQUIRED",
                "Reinitialize the runtime with an encryption key for full-trace consent",
            )
        self.consent = consent
        if downgraded:
            self._pending.clear()
            self._memory_records.clear()
            if self._storage_path:
                with self._connect() as connection:
                    connection.execute("DELETE FROM audit_ledger")
            if consent not in (Consent.ACTIVE, Consent.EXPLICIT):
                self._fernet = None


__all__ = ["AuditLedger", "PassiveAnonymizer"]
