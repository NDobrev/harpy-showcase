"""Runtime configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_DATABASE_PATH = "ledgerline.db"
DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100


@dataclass(frozen=True)
class Settings:
    database_path: str = DEFAULT_DATABASE_PATH
    page_size: int = DEFAULT_PAGE_SIZE
    allow_partial_capture: bool = True


def load_settings() -> Settings:
    return Settings(
        database_path=os.environ.get("LEDGERLINE_DATABASE", DEFAULT_DATABASE_PATH),
        page_size=int(os.environ.get("LEDGERLINE_PAGE_SIZE", DEFAULT_PAGE_SIZE)),
        allow_partial_capture=os.environ.get("LEDGERLINE_PARTIAL_CAPTURE", "1") == "1",
    )
