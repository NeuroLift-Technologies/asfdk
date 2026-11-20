"""At-most-once reservations with no locks held across adapter I/O."""
from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .crypto import canonical_json
from .errors import PolicyDenied
from .models import Consent, Reservation, TerminalState


class MemoryReservationStore:
    """Process-local store required under NONE consent."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._rows: Dict[str, Dict[str, Any]] = {}
        self._jti: Dict[Tuple[str, str], float] = {}

    def reserve(self, key: str, session_id: str, request_hash: str, exp: float) -> Reservation:
        with self._lock:
            now = time.time()
            self._rows = {k: row for k, row in self._rows.items() if row["exp"] > now}
            row = self._rows.get(key)
            if row is None:
                row = {"session_id": session_id, "request_hash": request_hash,
                       "state": "RESERVED", "response": None, "deferred": False, "exp": exp}
                self._rows[key] = row
                created = True
            else:
                created = False
            return self._view(key, row, created)

    def finalize(self, key: str, state: TerminalState, response: Any = None,
                 deferred: bool = False) -> None:
        with self._lock:
            if key not in self._rows:
                raise KeyError(key)
            self._rows[key].update(state=state.value, response=response, deferred=deferred)

    def deferred(self) -> List[Reservation]:
        with self._lock:
            return [self._view(key, row) for key, row in self._rows.items()
                    if row["state"] == "COMMITTED" and row["deferred"]]

    def mark_surfaced(self, keys: List[str]) -> None:
        with self._lock:
            for key in keys:
                if key in self._rows:
                    self._rows[key]["deferred"] = False

    def reserve_jti(self, jkt: str, jti: str, exp: float) -> bool:
        with self._lock:
            now = time.time()
            self._jti = {item: expiry for item, expiry in self._jti.items() if expiry > now}
            key = (jkt, jti)
            if key in self._jti:
                return False
            self._jti[key] = exp
            return True

    def clear(self) -> None:
        with self._lock:
            self._rows.clear()
            self._jti.clear()

    @staticmethod
    def _view(key: str, row: Dict[str, Any], created: bool = False) -> Reservation:
        return Reservation(key=key, session_id=row["session_id"],
                           request_hash=row["request_hash"], state=row["state"],
                           response=row["response"], deferred=row["deferred"], created=created)


class SQLiteReservationStore:
    """Local-first WAL store; each reservation is a short BEGIN IMMEDIATE transaction."""

    def __init__(self, path: str, *, response_cipher: Any = None,
                 retain_responses: bool = False) -> None:
        self.path = path
        self._response_cipher = response_cipher
        self._retain_responses = retain_responses
        Path(path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS reservations (
                    key TEXT PRIMARY KEY, session_id TEXT NOT NULL,
                    request_hash TEXT NOT NULL, state TEXT NOT NULL,
                    response_json TEXT, deferred INTEGER NOT NULL DEFAULT 0,
                    exp REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS dpop_jti (
                    jkt TEXT NOT NULL, jti TEXT NOT NULL, exp REAL NOT NULL,
                    PRIMARY KEY (jkt, jti)
                );
            """)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        connection.row_factory = sqlite3.Row
        return connection

    def _encode_response(self, response: Any) -> Optional[str]:
        if response is None or not self._retain_responses:
            return None
        serialized = canonical_json(response)
        if self._response_cipher is None:
            raise PolicyDenied("RESPONSE_ENCRYPTION_REQUIRED", "Full responses require encryption")
        return self._response_cipher.encrypt(serialized).decode("ascii")

    def _decode_response(self, stored: Optional[str]) -> Any:
        if not stored:
            return None
        if self._response_cipher is None:
            raise PolicyDenied("RESPONSE_DECRYPTION_UNAVAILABLE", "Response key is unavailable")
        from cryptography.fernet import InvalidToken
        try:
            return json.loads(self._response_cipher.decrypt(stored.encode("ascii")))
        except (InvalidToken, ValueError) as err:
            raise PolicyDenied("RESPONSE_INTEGRITY_ERROR", "Stored response cannot be verified") from err

    def _view(self, row: sqlite3.Row, created: bool = False) -> Reservation:
        return Reservation(
            key=row["key"], session_id=row["session_id"], request_hash=row["request_hash"],
            state=row["state"], response=self._decode_response(row["response_json"]),
            deferred=bool(row["deferred"]), created=created,
        )

    def reserve(self, key: str, session_id: str, request_hash: str, exp: float) -> Reservation:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("DELETE FROM reservations WHERE exp <= ?", (time.time(),))
            row = connection.execute("SELECT * FROM reservations WHERE key = ?", (key,)).fetchone()
            created = row is None
            if created:
                connection.execute(
                    "INSERT INTO reservations VALUES (?, ?, ?, 'RESERVED', NULL, 0, ?)",
                    (key, session_id, request_hash, exp),
                )
                row = connection.execute("SELECT * FROM reservations WHERE key = ?", (key,)).fetchone()
            connection.execute("COMMIT")
            return self._view(row, created)
        except Exception:
            if connection.in_transaction:
                connection.execute("ROLLBACK")
            raise
        finally:
            connection.close()

    def finalize(self, key: str, state: TerminalState, response: Any = None,
                 deferred: bool = False) -> None:
        response_json = self._encode_response(response)
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                "UPDATE reservations SET state = ?, response_json = ?, deferred = ? WHERE key = ?",
                (state.value, response_json, int(deferred), key),
            )
            if cursor.rowcount != 1:
                raise KeyError(key)
            connection.execute("COMMIT")

    def deferred(self) -> List[Reservation]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM reservations WHERE state = 'COMMITTED' AND deferred = 1"
            ).fetchall()
            return [self._view(row) for row in rows]

    def mark_surfaced(self, keys: List[str]) -> None:
        if not keys:
            return
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.executemany(
                "UPDATE reservations SET deferred = 0 WHERE key = ?", [(key,) for key in keys]
            )
            connection.execute("COMMIT")

    def reserve_jti(self, jkt: str, jti: str, exp: float) -> bool:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("DELETE FROM dpop_jti WHERE exp <= ?", (time.time(),))
            cursor = connection.execute(
                "INSERT OR IGNORE INTO dpop_jti (jkt, jti, exp) VALUES (?, ?, ?)",
                (jkt, jti, exp),
            )
            connection.execute("COMMIT")
            return cursor.rowcount == 1
        except Exception:
            if connection.in_transaction:
                connection.execute("ROLLBACK")
            raise
        finally:
            connection.close()

    def update_consent(self, consent: Consent, cipher: Any = None) -> None:
        retain = consent in (Consent.ACTIVE, Consent.EXPLICIT)
        if retain and cipher is None:
            raise PolicyDenied("RESPONSE_ENCRYPTION_REQUIRED", "Full responses require encryption")
        self._response_cipher = cipher
        self._retain_responses = retain
        if not retain:
            with self._connect() as connection:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute("UPDATE reservations SET response_json = NULL")
                connection.execute("COMMIT")

    def clear(self) -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("DELETE FROM reservations")
            connection.execute("DELETE FROM dpop_jti")
            connection.execute("COMMIT")


def request_hash(payload: Any) -> str:
    from .crypto import sha256
    try:
        return sha256(canonical_json(payload))
    except (TypeError, ValueError) as err:
        raise PolicyDenied("INVALID_REQUEST", "Write payload must be JSON serializable") from err


def validate_reservation(reservation: Reservation, session_id: str, expected_hash: str) -> None:
    if reservation.session_id != session_id or reservation.request_hash != expected_hash:
        raise PolicyDenied("IDEMPOTENCY_CONFLICT", "Idempotency key was reused for a different request")


__all__ = [
    "MemoryReservationStore", "SQLiteReservationStore", "request_hash", "validate_reservation",
]
