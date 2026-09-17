from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest

from ledgerline.auth.permissions import Principal
from ledgerline.db.session import connect, migrate


@pytest.fixture()
def connection() -> Iterator[sqlite3.Connection]:
    conn = connect(":memory:")
    migrate(conn)
    yield conn
    conn.close()


@pytest.fixture()
def agent() -> Principal:
    return Principal(user_id="u_agent", role="agent")


@pytest.fixture()
def admin() -> Principal:
    return Principal(user_id="u_admin", role="admin")
