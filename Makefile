.PHONY: setup test spec client check

setup:
	uv sync --extra dev

test:
	uv run pytest -q

spec:
	uv run python scripts/dump_openapi.py

client:
	ledgerline-codegen --spec openapi.json --out src/ledgerline/generated/openapi_client.py

check: test spec
	git diff --exit-code openapi.json
