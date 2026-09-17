"""Customer SQL."""

from __future__ import annotations

import sqlite3

from ledgerline.db.models import CustomerRow

INSERT_CUSTOMER = """
INSERT INTO customers (id, email, created_at)
VALUES (?, ?, ?)
ON CONFLICT (email) DO NOTHING
"""

SELECT_BY_EMAIL = "SELECT * FROM customers WHERE email = ?"
SELECT_BY_ID = "SELECT * FROM customers WHERE id = ?"


def insert_customer(connection: sqlite3.Connection, customer: CustomerRow) -> None:
    connection.execute(
        INSERT_CUSTOMER,
        (customer.id, customer.email, customer.created_at),
    )


def get_by_email(connection: sqlite3.Connection, email: str) -> CustomerRow | None:
    row = connection.execute(SELECT_BY_EMAIL, (email,)).fetchone()
    return CustomerRow.from_row(row) if row else None


def get_by_id(connection: sqlite3.Connection, customer_id: str) -> CustomerRow | None:
    row = connection.execute(SELECT_BY_ID, (customer_id,)).fetchone()
    return CustomerRow.from_row(row) if row else None
