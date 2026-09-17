from __future__ import annotations

import pytest

from ledgerline.db.session import MIGRATIONS_DIR, applied_versions, connect, migrate

LEGACY_INVOICE = """
INSERT INTO invoices (
    id, customer_email, region, status,
    subtotal_cents, discount_cents, tax_cents, total_cents, created_at
) VALUES (?, ?, 'XX', 'open', 5000, 0, 0, 5000, ?)
"""


@pytest.fixture()
def legacy_connection():
    """A database on 0001 only, holding invoices with inline customer emails."""
    conn = connect(":memory:")
    conn.executescript((MIGRATIONS_DIR / "0001_initial.sql").read_text(encoding="utf-8"))
    applied_versions(conn)
    conn.execute("INSERT INTO schema_version (version) VALUES ('0001_initial')")
    conn.execute(LEGACY_INVOICE, ("inv_a", "ops@acme.test", "2026-01-01T00:00:00+00:00"))
    conn.execute(LEGACY_INVOICE, ("inv_b", "ops@acme.test", "2026-02-01T00:00:00+00:00"))
    conn.execute(LEGACY_INVOICE, ("inv_c", "other@acme.test", "2026-03-01T00:00:00+00:00"))
    conn.commit()
    yield conn
    conn.close()


def test_backfill_creates_one_customer_per_email(legacy_connection):
    migrate(legacy_connection)

    emails = legacy_connection.execute("SELECT email FROM customers ORDER BY email").fetchall()
    assert [row["email"] for row in emails] == ["ops@acme.test", "other@acme.test"]


def test_backfill_links_every_existing_invoice(legacy_connection):
    migrate(legacy_connection)

    rows = legacy_connection.execute(
        """
        SELECT invoices.id AS invoice_id, customers.email AS email
        FROM invoices
        JOIN customers ON customers.id = invoices.customer_id
        ORDER BY invoices.id
        """
    ).fetchall()

    assert [(row["invoice_id"], row["email"]) for row in rows] == [
        ("inv_a", "ops@acme.test"),
        ("inv_b", "ops@acme.test"),
        ("inv_c", "other@acme.test"),
    ]


def test_dropped_column_is_gone(legacy_connection):
    migrate(legacy_connection)

    columns = {
        row["name"] for row in legacy_connection.execute("PRAGMA table_info(invoices)").fetchall()
    }
    assert "customer_email" not in columns
    assert "customer_id" in columns


def test_migrations_are_applied_once(legacy_connection):
    assert migrate(legacy_connection) == ["0002_customers"]
    assert migrate(legacy_connection) == []
