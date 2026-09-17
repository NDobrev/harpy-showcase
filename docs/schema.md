# Database

SQLite locally, PostgreSQL-compatible DDL in `migrations/versions/`. Migrations
are forward only and applied in filename order; applied versions are recorded in
`schema_version`.

| Table | Purpose |
|---|---|
| `invoices` | One row per invoice with its priced totals and status |
| `invoice_items` | Line items belonging to an invoice |
| `payments` | Captures and refunds, distinguished by `kind` |
| `ledger_entries` | Double entry rows for every captured or refunded amount |

`invoices.customer_email` is the only customer identity we store today, which is
why invoices cannot be grouped per customer yet.
