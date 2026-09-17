# Database

SQLite locally, PostgreSQL-compatible DDL in `migrations/versions/`. Migrations
are forward only and applied in filename order; applied versions are recorded in
`schema_version`.

| Table | Purpose |
|---|---|
| `customers` | One row per customer email, referenced by invoices |
| `invoices` | One row per invoice with its priced totals and status |
| `invoice_items` | Line items belonging to an invoice |
| `payments` | Captures and refunds, distinguished by `kind` |
| `ledger_entries` | Double entry rows for every captured or refunded amount |

## Customer identity

`invoices.customer_id` references `customers.id`; `customers.email` is unique.
Reads join the two tables and keep exposing `customer_email`, so the HTTP
responses did not change when the column moved.

`invoices.customer_email` was **dropped** in `0002_customers`. The migration
backfills one customer per distinct email first, so no address is lost, but the
column cannot be recovered by rolling the code back — only by restoring a
backup.
