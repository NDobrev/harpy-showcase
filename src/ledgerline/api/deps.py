"""Request scoped dependencies: settings, database connection, principal."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from functools import lru_cache

from fastapi import Header, HTTPException

from ledgerline.auth.permissions import ROLE_PERMISSIONS, Principal
from ledgerline.config import Settings, load_settings
from ledgerline.db.session import connect, migrate


@lru_cache(maxsize=1)
def settings() -> Settings:
    return load_settings()


def get_connection() -> Iterator[sqlite3.Connection]:
    connection = connect(settings().database_path)
    migrate(connection)
    try:
        yield connection
    finally:
        connection.close()


def get_principal(
    x_user_id: str = Header(default=""),
    x_user_role: str = Header(default=""),
) -> Principal:
    """Trusted-header identity. The gateway terminates real authentication."""
    if not x_user_id or x_user_role not in ROLE_PERMISSIONS:
        raise HTTPException(status_code=401, detail="unknown principal")
    return Principal(user_id=x_user_id, role=x_user_role)
