"""Invoice use cases."""

from __future__ import annotations

import base64
import binascii
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from ledgerline.auth.permissions import INVOICE_READ, INVOICE_WRITE, Principal, authorize
from ledgerline.config import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
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


@dataclass(frozen=True)
class InvoicePage:
    invoices: list[InvoiceRow]
    next_cursor: str | None


class InvoiceNotFound(LookupError):
    """Raised when an invoice id does not exist."""


class InvalidCursor(ValueError):
    """Raised when a pagination cursor cannot be decoded."""


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


def _encode_cursor(invoice: InvoiceRow) -> str:
    raw = f"{invoice.created_at}|{invoice.id}".encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _decode_cursor(cursor: str) -> tuple[str, str]:
    padded = cursor + "=" * (-len(cursor) % 4)
    try:
        created_at, invoice_id = base64.urlsafe_b64decode(padded).decode().split("|", 1)
    except (binascii.Error, UnicodeDecodeError, ValueError) as error:
        raise InvalidCursor(cursor) from error
    return created_at, invoice_id


def list_invoices(
    connection: sqlite3.Connection,
    principal: Principal,
    *,
    limit: int = DEFAULT_PAGE_SIZE,
    cursor: str | None = None,
) -> InvoicePage:
    """Return one page of invoices, newest first, plus the cursor for the next."""
    authorize(principal, INVOICE_READ)
    if limit < 1 or limit > MAX_PAGE_SIZE:
        raise ValueError(f"limit must be between 1 and {MAX_PAGE_SIZE}")
    after = _decode_cursor(cursor) if cursor else None
    rows = invoice_repo.list_invoice_page(connection, limit=limit + 1, after=after)
    has_more = len(rows) > limit
    page = rows[:limit]
    return InvoicePage(
        invoices=page,
        next_cursor=_encode_cursor(page[-1]) if has_more and page else None,
    )
