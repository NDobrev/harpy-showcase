"""Connection handling and forward-only migrations."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).resolve().parents[3] / "migrations" / "versions"

SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    version    TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
)
"""


def connect(database_path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def transaction(connection: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    try:
        yield connection
    except Exception:
        connection.rollback()
        raise
    connection.commit()


def applied_versions(connection: sqlite3.Connection) -> set[str]:
    connection.execute(SCHEMA_VERSION_TABLE)
    rows = connection.execute("SELECT version FROM schema_version").fetchall()
    return {row["version"] for row in rows}


def migrate(connection: sqlite3.Connection, *, migrations_dir: Path | None = None) -> list[str]:
    """Apply every migration that has not run yet, in filename order."""
    directory = migrations_dir or MIGRATIONS_DIR
    already = applied_versions(connection)
    applied: list[str] = []
    for script in sorted(directory.glob("*.sql")):
        version = script.stem
        if version in already:
            continue
        with transaction(connection):
            connection.executescript(script.read_text(encoding="utf-8"))
            connection.execute("INSERT INTO schema_version (version) VALUES (?)", (version,))
        applied.append(version)
    return applied
