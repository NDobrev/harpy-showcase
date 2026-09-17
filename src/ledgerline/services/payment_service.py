"""Capture and refund use cases."""

from __future__ import annotations

import sqlite3
import uuid
from datetime import date, datetime, timezone

from ledgerline.auth.permissions import (
    PAYMENT_CAPTURE,
    REFUND_ISSUE,
    Principal,
    authorize,
)
from ledgerline.db.models import PaymentRow
from ledgerline.db.repositories import invoices as invoice_repo
from ledgerline.db.repositories import payments as payment_repo
from ledgerline.domain.ledger import capture_entries, refund_entries
from ledgerline.domain.refunds import RefundRejected, RefundRequest, check_refund
from ledgerline.services.invoice_service import (
    STATUS_PAID,
    STATUS_REFUNDED,
    InvoiceNotFound,
)

KIND_CAPTURE = "capture"
KIND_REFUND = "refund"


class CaptureRejected(ValueError):
    """Raised when a capture is not allowed."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def capture_payment(
    connection: sqlite3.Connection,
    principal: Principal,
    invoice_id: str,
    amount_cents: int,
) -> PaymentRow:
    authorize(principal, PAYMENT_CAPTURE)
    invoice = invoice_repo.get_invoice(connection, invoice_id)
    if invoice is None:
        raise InvoiceNotFound(invoice_id)
    captured = payment_repo.total_by_kind(connection, invoice_id, KIND_CAPTURE)
    outstanding = invoice.total_cents - captured
    if amount_cents <= 0:
        raise CaptureRejected("capture amount must be positive")
    if amount_cents > outstanding:
        raise CaptureRejected(f"only {outstanding} cents are outstanding on this invoice")
    payment = PaymentRow(
        id=f"pay_{uuid.uuid4().hex[:12]}",
        invoice_id=invoice_id,
        kind=KIND_CAPTURE,
        amount_cents=amount_cents,
        created_at=_now(),
    )
    payment_repo.insert_payment(connection, payment)
    payment_repo.insert_ledger_entries(
        connection,
        capture_entries(invoice_id, amount_cents, payment_id=payment.id),
    )
    if amount_cents == outstanding:
        invoice_repo.set_status(connection, invoice_id, STATUS_PAID)
    connection.commit()
    return payment


def issue_refund(
    connection: sqlite3.Connection,
    principal: Principal,
    request: RefundRequest,
    *,
    today: date | None = None,
) -> PaymentRow:
    authorize(principal, REFUND_ISSUE)
    invoice = invoice_repo.get_invoice(connection, request.invoice_id)
    if invoice is None:
        raise InvoiceNotFound(request.invoice_id)
    captures = payment_repo.list_payments(connection, request.invoice_id)
    first_capture = next((row for row in captures if row.kind == KIND_CAPTURE), None)
    if first_capture is None:
        raise RefundRejected("invoice has no captured payment")
    captured = payment_repo.total_by_kind(connection, request.invoice_id, KIND_CAPTURE)
    refunded = payment_repo.total_by_kind(connection, request.invoice_id, KIND_REFUND)
    amount = check_refund(
        request,
        captured_cents=captured,
        refunded_cents=refunded,
        captured_on=date.fromisoformat(first_capture.created_at[:10]),
        today=today or datetime.now(timezone.utc).date(),
    )
    payment = PaymentRow(
        id=f"ref_{uuid.uuid4().hex[:12]}",
        invoice_id=request.invoice_id,
        kind=KIND_REFUND,
        amount_cents=amount,
        created_at=_now(),
    )
    payment_repo.insert_payment(connection, payment)
    payment_repo.insert_ledger_entries(
        connection,
        refund_entries(request.invoice_id, amount, payment_id=payment.id),
    )
    if refunded + amount == captured:
        invoice_repo.set_status(connection, request.invoice_id, STATUS_REFUNDED)
    connection.commit()
    return payment
