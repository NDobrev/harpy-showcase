"""Application factory."""

from __future__ import annotations

from fastapi import FastAPI

from ledgerline import __version__
from ledgerline.api.routes import health, invoices, payments


def create_app() -> FastAPI:
    app = FastAPI(title="Ledgerline", version=__version__)
    app.include_router(health.router)
    app.include_router(invoices.router)
    app.include_router(payments.router)
    return app


app = create_app()
