"""Invoice use cases."""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from ledgerline.auth.permissions import INVOICE_READ, INVOICE_WRITE, Principal, authorize
from ledgerline.db.models import InvoiceItemRow, InvoiceRow
from ledgerline.db.repositories import invoices as invoice_repo
from ledgerline.domain.pricing import LineItem, price_invoice

STATUS_OPEN = "open"
STATUS_PAID = "paid"
STATUS_REFUNDED = "refunded"


@dataclass(frozen=True)
class NewInvoice:
    customer_email: str
    region: str
    items: list[LineItem]
    discount_percent: float = 0.0


class InvoiceNotFound(LookupError):
    """Raised when an invoice id does not exist."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def create_invoice(
    connection: sqlite3.Connection,
    principal: Principal,
    request: NewInvoice,
) -> InvoiceRow:
    authorize(principal, INVOICE_WRITE)
    totals = price_invoice(
        request.items,
        region=request.region,
        discount_percent=request.discount_percent,
    )
    invoice = InvoiceRow(
        id=f"inv_{uuid.uuid4().hex[:12]}",
        customer_email=request.customer_email,
        region=request.region,
        status=STATUS_OPEN,
        subtotal_cents=totals.subtotal_cents,
        discount_cents=totals.discount_cents,
        tax_cents=totals.tax_cents,
        total_cents=totals.total_cents,
        created_at=_now(),
    )
    invoice_repo.insert_invoice(connection, invoice)
    invoice_repo.insert_items(
        connection,
        invoice.id,
        [(item.description, item.quantity, item.unit_amount_cents) for item in request.items],
    )
    connection.commit()
    return invoice


def get_invoice(
    connection: sqlite3.Connection,
    principal: Principal,
    invoice_id: str,
) -> tuple[InvoiceRow, list[InvoiceItemRow]]:
    authorize(principal, INVOICE_READ)
    invoice = invoice_repo.get_invoice(connection, invoice_id)
    if invoice is None:
        raise InvoiceNotFound(invoice_id)
    return invoice, invoice_repo.list_items(connection, invoice_id)


def list_invoices(connection: sqlite3.Connection, principal: Principal) -> list[InvoiceRow]:
    authorize(principal, INVOICE_READ)
    return invoice_repo.list_invoices(connection)
