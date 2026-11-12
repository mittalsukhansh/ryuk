"""Checksummed, forward-only SQLite migrations. Never drop or reset financial rows."""

import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DIRECTORY = Path(__file__).resolve().parents[1] / "migrations"


def _statements(text: str) -> list[str]:
    statements = []
    pending = ""
    for line in text.splitlines(keepends=True):
        pending += line
        if sqlite3.complete_statement(pending):
            statements.append(pending)
            pending = ""
    if pending.strip():
        raise ValueError("Incomplete migration statement")
    return statements


def migrate(connection: sqlite3.Connection) -> None:
    """Apply all pending versions in one transaction; reject drift/newer schemas."""
    files = sorted(DIRECTORY.glob("[0-9][0-9][0-9]_*.sql"))
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA synchronous=FULL")
    connection.execute("BEGIN IMMEDIATE")
    try:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            "version INTEGER PRIMARY KEY, checksum TEXT NOT NULL, applied_at TEXT NOT NULL)"
        )
        applied = dict(connection.execute("SELECT version,checksum FROM schema_migrations"))
        versions = {int(path.name[:3]) for path in files}
        if set(applied) - versions:
            raise ValueError("Database schema is newer than this application")
        # Validate baseline legacy table shapes before adopting an unversioned ledger.
        if not applied:
            required = {
                "accounts": {"user_id", "currency", "limit_minor", "settled_minor"},
                "policies": {"user_id", "body"},
                "merchants": {"merchant_id", "paypal_id"},
                "checkouts": {"payment_id", "proposal_id", "user_id", "body"},
                "reservations": {"payment_id", "user_id", "currency", "amount_minor", "status"},
                "checkout_audit": {"sequence", "payment_id", "event", "at", "details"},
            }
            for table, columns in required.items():
                actual = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
                if actual and not columns.issubset(actual):
                    raise ValueError("Legacy database schema is incompatible")
        for path in files:
            version = int(path.name[:3])
            raw = path.read_text(encoding="utf-8").encode()
            checksum = hashlib.sha256(raw).hexdigest()
            if version in applied:
                if applied[version] != checksum:
                    raise ValueError("Applied database migration checksum mismatch")
                continue
            if applied and version < max(applied):
                raise ValueError("Database migration history has a gap")
            for statement in _statements(raw.decode()):
                connection.execute(statement)
            connection.execute(
                "INSERT INTO schema_migrations VALUES (?,?,?)",
                (
                    version,
                    checksum,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
        connection.execute(
            "INSERT OR IGNORE INTO recovery_index(proposal_id,user_id) "
            "SELECT proposal_id,user_id FROM checkouts ORDER BY rowid"
        )
        if connection.execute("PRAGMA foreign_key_check").fetchone() is not None:
            raise ValueError("Database foreign-key integrity check failed")
        connection.commit()
    except BaseException:
        connection.rollback()
        raise
