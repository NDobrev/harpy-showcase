"""Row shapes for the tables created by the SQL migrations."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

CUSTOMERS_TABLE = "customers"
INVOICES_TABLE = "invoices"
INVOICE_ITEMS_TABLE = "invoice_items"
PAYMENTS_TABLE = "payments"
LEDGER_ENTRIES_TABLE = "ledger_entries"

INVOICE_COLUMNS = (
    "id",
    "customer_id",
    "region",
    "status",
    "subtotal_cents",
    "discount_cents",
    "tax_cents",
    "total_cents",
    "created_at",
)


@dataclass(frozen=True)
class CustomerRow:
    id: str
    email: str
    created_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> CustomerRow:
        return cls(id=row["id"], email=row["email"], created_at=row["created_at"])


@dataclass(frozen=True)
class InvoiceRow:
    id: str
    customer_id: str
    region: str
    status: str
    subtotal_cents: int
    discount_cents: int
    tax_cents: int
    total_cents: int
    created_at: str
    customer_email: str = ""
    """Joined from `customers`; not a column on `invoices`."""

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> InvoiceRow:
        values = {column: row[column] for column in INVOICE_COLUMNS}
        email = row["customer_email"] if "customer_email" in row.keys() else ""
        return cls(**values, customer_email=email)


@dataclass(frozen=True)
class InvoiceItemRow:
    id: int
    invoice_id: str
    description: str
    quantity: int
    unit_amount_cents: int

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> InvoiceItemRow:
        return cls(
            id=row["id"],
            invoice_id=row["invoice_id"],
            description=row["description"],
            quantity=row["quantity"],
            unit_amount_cents=row["unit_amount_cents"],
        )


@dataclass(frozen=True)
class PaymentRow:
    id: str
    invoice_id: str
    kind: str
    amount_cents: int
    created_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> PaymentRow:
        return cls(
            id=row["id"],
            invoice_id=row["invoice_id"],
            kind=row["kind"],
            amount_cents=row["amount_cents"],
            created_at=row["created_at"],
        )
