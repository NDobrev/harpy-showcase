-- 0001_initial: invoices, line items, payments, and ledger entries.

CREATE TABLE IF NOT EXISTS invoices (
    id              TEXT    PRIMARY KEY,
    customer_email  TEXT    NOT NULL,
    region          TEXT    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'open',
    subtotal_cents  INTEGER NOT NULL,
    discount_cents  INTEGER NOT NULL DEFAULT 0,
    tax_cents       INTEGER NOT NULL DEFAULT 0,
    total_cents     INTEGER NOT NULL,
    created_at      TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS invoice_items (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id         TEXT    NOT NULL REFERENCES invoices (id) ON DELETE CASCADE,
    description        TEXT    NOT NULL,
    quantity           INTEGER NOT NULL,
    unit_amount_cents  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS payments (
    id           TEXT    PRIMARY KEY,
    invoice_id   TEXT    NOT NULL REFERENCES invoices (id) ON DELETE CASCADE,
    kind         TEXT    NOT NULL,
    amount_cents INTEGER NOT NULL,
    created_at   TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS ledger_entries (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id   TEXT    NOT NULL REFERENCES invoices (id) ON DELETE CASCADE,
    account      TEXT    NOT NULL,
    debit_cents  INTEGER NOT NULL DEFAULT 0,
    credit_cents INTEGER NOT NULL DEFAULT 0,
    memo         TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS invoices_customer_email_idx ON invoices (customer_email);
CREATE INDEX IF NOT EXISTS payments_invoice_id_idx ON payments (invoice_id);
