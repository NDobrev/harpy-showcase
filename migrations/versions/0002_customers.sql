-- 0002_customers: give customers their own row and point invoices at it.
--
-- Invoices stored the customer email inline, so two invoices for the same
-- person had no relationship. This creates `customers`, backfills one row per
-- distinct email, rewires `invoices` through `customer_id`, and drops the
-- inline column.

CREATE TABLE IF NOT EXISTS customers (
    id         TEXT PRIMARY KEY,
    email      TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS customers_email_key ON customers (email);

ALTER TABLE invoices ADD COLUMN customer_id TEXT REFERENCES customers (id);

INSERT INTO customers (id, email, created_at)
SELECT 'cus_' || lower(hex(randomblob(6))), customer_email, min(created_at)
FROM invoices
GROUP BY customer_email;

UPDATE invoices
SET customer_id = (SELECT id FROM customers WHERE customers.email = invoices.customer_email);

DROP INDEX IF EXISTS invoices_customer_email_idx;

ALTER TABLE invoices DROP COLUMN customer_email;

CREATE INDEX IF NOT EXISTS invoices_customer_id_idx ON invoices (customer_id);
