"""Write the OpenAPI document the routers produce to openapi.json."""

from __future__ import annotations

import json
from pathlib import Path

from ledgerline.api.app import create_app

OUTPUT = Path(__file__).resolve().parents[1] / "openapi.json"


def main() -> None:
    OUTPUT.write_text(
        json.dumps(create_app().openapi(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
