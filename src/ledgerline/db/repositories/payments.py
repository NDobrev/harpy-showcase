"""Payment and ledger SQL."""

from __future__ import annotations

import sqlite3

from ledgerline.db.models import PaymentRow
from ledgerline.domain.ledger import LedgerEntry

INSERT_PAYMENT = """
INSERT INTO payments (id, invoice_id, kind, amount_cents, created_at)
VALUES (?, ?, ?, ?, ?)
"""

INSERT_LEDGER_ENTRY = """
INSERT INTO ledger_entries (invoice_id, account, debit_cents, credit_cents, memo)
VALUES (?, ?, ?, ?, ?)
"""

SELECT_PAYMENTS = "SELECT * FROM payments WHERE invoice_id = ? ORDER BY created_at, id"
SUM_BY_KIND = """
SELECT COALESCE(SUM(amount_cents), 0) AS total
FROM payments
WHERE invoice_id = ? AND kind = ?
"""


def insert_payment(conn: sqlite3.Connection, payment: PaymentRow) -> None:
    conn.execute(
        INSERT_PAYMENT,
        (
            payment.id,
            payment.invoice_id,
            payment.kind,
            payment.amount_cents,
            payment.created_at,
        ),
    )


def insert_ledger_entries(conn: sqlite3.Connection, entries: list[LedgerEntry]) -> None:
    conn.executemany(
        INSERT_LEDGER_ENTRY,
        [
            (entry.invoice_id, entry.account, entry.debit_cents, entry.credit_cents, entry.memo)
            for entry in entries
        ],
    )


def list_payments(conn: sqlite3.Connection, invoice_id: str) -> list[PaymentRow]:
    rows = conn.execute(SELECT_PAYMENTS, (invoice_id,)).fetchall()
    return [PaymentRow.from_row(row) for row in rows]


def total_by_kind(conn: sqlite3.Connection, invoice_id: str, kind: str) -> int:
    row = conn.execute(SUM_BY_KIND, (invoice_id, kind)).fetchone()
    return int(row["total"])
