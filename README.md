# Ledgerline — a showcase repository for [Harpy](https://github.com/NDobrev/harpy)

A small invoicing and payments service that exists so Harpy has realistic pull
requests to review. Nothing here is production software; the interesting part is
the pull request history.

> **Harpy** is a terminal PR reviewer that turns sprawling diffs into ranked,
> evidence-backed logical changes. Review the decisions, not the diff volume.

## Showcase pull requests

Each pull request isolates one kind of change so the corresponding Harpy lens
has something concrete to explain.

| PR | Kind of change | What Harpy should surface |
|---|---|---|
| 1 | Endpoint / API contract | A removed route, a changed response shape, and a new refund endpoint — a breaking API impact |
| 2 | Database schema | A new table, a new foreign key, a dropped column, and the queries that follow — a breaking DB impact |
| 3 | Business logic | Discount proration and rounding change the money customers owe, with one untested edge case |
| 4 | Security, buried in noise | An agent refund permission and a removed amount ceiling, hidden inside a large mechanical refactor |

Review them with:

```bash
harpy --repo NDobrev/harpy-showcase <PR>
```

## Layout

| Location | Contents |
|---|---|
| `src/ledgerline/api/` | FastAPI routers, request/response schemas, dependencies |
| `src/ledgerline/auth/` | Roles and permission checks |
| `src/ledgerline/db/` | Row shapes, connections, migration runner, SQL repositories |
| `src/ledgerline/domain/` | Pure pricing, refund, and ledger rules |
| `src/ledgerline/services/` | Use cases combining domain rules with storage |
| `migrations/versions/` | Forward-only SQL migrations |
| `src/ledgerline/generated/` | Generated OpenAPI client — do not hand-edit |
| `tests/` | Domain and service tests |
| `scripts/` | Spec dump and code generation helpers |
| `docs/` | API and schema reference |

## Run it

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
pytest
uvicorn ledgerline.api.app:app --reload
```

Money is always an integer number of cents. Identity arrives from the gateway as
`X-User-Id` and `X-User-Role` headers:

```bash
curl -s localhost:8000/v1/invoices \
  -H 'X-User-Id: u_1' -H 'X-User-Role: agent' \
  -H 'content-type: application/json' \
  -d '{"customer_email":"ops@acme.test","region":"US-CA",
       "items":[{"description":"Team seat","quantity":3,"unit_amount_cents":1999}],
       "discount_percent":10}'
```

See [docs/api.md](docs/api.md) and [docs/schema.md](docs/schema.md).
