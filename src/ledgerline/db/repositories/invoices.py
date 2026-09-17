"""Invoice and line item SQL."""

from __future__ import annotations

import sqlite3

from ledgerline.db.models import InvoiceItemRow, InvoiceRow

INSERT_INVOICE = """
INSERT INTO invoices (
    id, customer_id, region, status,
    subtotal_cents, discount_cents, tax_cents, total_cents, created_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

INSERT_ITEM = """
INSERT INTO invoice_items (invoice_id, description, quantity, unit_amount_cents)
VALUES (?, ?, ?, ?)
"""

INVOICE_WITH_CUSTOMER = """
SELECT invoices.*, customers.email AS customer_email
FROM invoices
LEFT JOIN customers ON customers.id = invoices.customer_id
"""

SELECT_INVOICE = f"{INVOICE_WITH_CUSTOMER} WHERE invoices.id = ?"
SELECT_ALL_INVOICES = f"{INVOICE_WITH_CUSTOMER} ORDER BY invoices.created_at DESC, invoices.id DESC"
SELECT_INVOICES_FOR_CUSTOMER = f"""
{INVOICE_WITH_CUSTOMER}
WHERE invoices.customer_id = ?
ORDER BY invoices.created_at DESC, invoices.id DESC
"""
SELECT_ITEMS = "SELECT * FROM invoice_items WHERE invoice_id = ? ORDER BY id"
UPDATE_STATUS = "UPDATE invoices SET status = ? WHERE id = ?"


def insert_invoice(connection: sqlite3.Connection, invoice: InvoiceRow) -> None:
    connection.execute(
        INSERT_INVOICE,
        (
            invoice.id,
            invoice.customer_id,
            invoice.region,
            invoice.status,
            invoice.subtotal_cents,
            invoice.discount_cents,
            invoice.tax_cents,
            invoice.total_cents,
            invoice.created_at,
        ),
    )


def insert_items(
    connection: sqlite3.Connection,
    invoice_id: str,
    items: list[tuple[str, int, int]],
) -> None:
    connection.executemany(
        INSERT_ITEM,
        [(invoice_id, description, quantity, unit) for description, quantity, unit in items],
    )


def get_invoice(connection: sqlite3.Connection, invoice_id: str) -> InvoiceRow | None:
    row = connection.execute(SELECT_INVOICE, (invoice_id,)).fetchone()
    return InvoiceRow.from_row(row) if row else None


def list_invoices(connection: sqlite3.Connection) -> list[InvoiceRow]:
    rows = connection.execute(SELECT_ALL_INVOICES).fetchall()
    return [InvoiceRow.from_row(row) for row in rows]


def list_invoices_for_customer(
    connection: sqlite3.Connection, customer_id: str
) -> list[InvoiceRow]:
    rows = connection.execute(SELECT_INVOICES_FOR_CUSTOMER, (customer_id,)).fetchall()
    return [InvoiceRow.from_row(row) for row in rows]


def list_items(connection: sqlite3.Connection, invoice_id: str) -> list[InvoiceItemRow]:
    rows = connection.execute(SELECT_ITEMS, (invoice_id,)).fetchall()
    return [InvoiceItemRow.from_row(row) for row in rows]


def set_status(connection: sqlite3.Connection, invoice_id: str, status: str) -> None:
    connection.execute(UPDATE_STATUS, (status, invoice_id))
