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
| [1](https://github.com/NDobrev/harpy-showcase/pull/1) | Endpoint / API contract | A removed route, a bare array becoming a paginated envelope, and a new refund endpoint — a breaking API impact |
| [2](https://github.com/NDobrev/harpy-showcase/pull/2) | Database schema | A new table, a new foreign key, a backfill, and a dropped column, with reads rewritten to a join — a breaking DB impact behind an unchanged HTTP contract |
| [3](https://github.com/NDobrev/harpy-showcase/pull/3) | Business logic | Discount proration and per-line rounding move the tax base, so totals change by up to −987 cents — and by +1 cent even with no discount |
| [4](https://github.com/NDobrev/harpy-showcase/pull/4) | Security, buried in noise | 1271 inserted lines, of which ~10 matter: agents gain `refund:issue`, the admin-only amount ceiling disappears, and a test asserting the old rule is flipped |

Review them with:

```bash
harpy --repo NDobrev/harpy-showcase <PR>
```

PR 4 is the one worth watching: the deliberate signal-to-noise ratio is about
1:130, the permission change is described as a one-line simplification in the PR
body, and the only test that guarded the old behavior was rewritten to assert
the new one.

## Layout

| Location | Contents |
|---|---|
| `src/ledgerline/api/` | FastAPI routers, request/response schemas, dependencies |
| `src/ledgerline/auth/` | Roles and permission checks |
| `src/ledgerline/db/` | Row shapes, connections, migration runner, SQL repositories |
| `src/ledgerline/domain/` | Pure pricing, refund, and ledger rules |
| `src/ledgerline/services/` | Use cases combining domain rules with storage |
| `migrations/versions/` | Forward-only SQL migrations |
| `tests/` | Domain and service tests |
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
