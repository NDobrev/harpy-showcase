"""Liveness and readiness."""

from __future__ import annotations

import sqlite3

from fastapi import APIRouter, Depends

from ledgerline import __version__
from ledgerline.api.deps import get_connection

router = APIRouter(tags=["health"])


@router.get("/v1/health")
def health() -> dict[str, str]:
    """Liveness. Does not touch the database."""
    return {"status": "ok", "version": __version__}


@router.get("/v1/health/ready")
def ready(connection: sqlite3.Connection = Depends(get_connection)) -> dict[str, str]:
    """Readiness. Runs a trivial query against the database."""
    connection.execute("SELECT 1").fetchone()
    return {"status": "ready"}
