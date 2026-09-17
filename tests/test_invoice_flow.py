from __future__ import annotations

import pytest

from ledgerline.auth.permissions import PermissionDenied, Principal
from ledgerline.db.repositories import payments as payment_repo
from ledgerline.domain.ledger import balance_cents, capture_entries, refund_entries
from ledgerline.domain.pricing import LineItem
from ledgerline.domain.refunds import RefundRequest
from ledgerline.services import invoice_service, payment_service
from ledgerline.services.invoice_service import NewInvoice

ITEMS = [LineItem("Team seat", 2, 2_500)]


def _new_invoice(discount_percent: float = 0.0) -> NewInvoice:
    return NewInvoice(
        customer_email="ops@acme.test",
        region="XX",
        items=ITEMS,
        discount_percent=discount_percent,
    )


def test_create_invoice_persists_totals_and_items(connection, agent):
    invoice = invoice_service.create_invoice(connection, agent, _new_invoice())

    stored, items = invoice_service.get_invoice(connection, agent, invoice.id)

    assert stored.total_cents == 5_000
    assert stored.status == invoice_service.STATUS_OPEN
    assert [item.description for item in items] == ["Team seat"]


def test_viewer_cannot_create_an_invoice(connection):
    viewer = Principal(user_id="u_viewer", role="viewer")

    with pytest.raises(PermissionDenied):
        invoice_service.create_invoice(connection, viewer, _new_invoice())


def test_full_capture_marks_the_invoice_paid(connection, agent):
    invoice = invoice_service.create_invoice(connection, agent, _new_invoice())

    payment_service.capture_payment(connection, agent, invoice.id, 5_000)

    stored, _items = invoice_service.get_invoice(connection, agent, invoice.id)
    assert stored.status == invoice_service.STATUS_PAID


def test_capture_above_outstanding_is_rejected(connection, agent):
    invoice = invoice_service.create_invoice(connection, agent, _new_invoice())

    with pytest.raises(payment_service.CaptureRejected):
        payment_service.capture_payment(connection, agent, invoice.id, 5_001)


def test_agent_cannot_issue_a_refund(connection, agent):
    invoice = invoice_service.create_invoice(connection, agent, _new_invoice())
    payment_service.capture_payment(connection, agent, invoice.id, 5_000)

    with pytest.raises(PermissionDenied):
        payment_service.issue_refund(
            connection, agent, RefundRequest(invoice.id, 1_000, "goodwill")
        )


def test_admin_refund_records_payment_and_status(connection, agent, admin):
    invoice = invoice_service.create_invoice(connection, agent, _new_invoice())
    payment_service.capture_payment(connection, agent, invoice.id, 5_000)

    payment_service.issue_refund(connection, admin, RefundRequest(invoice.id, 5_000, "goodwill"))

    stored, _items = invoice_service.get_invoice(connection, agent, invoice.id)
    assert stored.status == invoice_service.STATUS_REFUNDED
    assert payment_repo.total_by_kind(connection, invoice.id, payment_service.KIND_REFUND) == 5_000


def test_invoice_page_walks_the_cursor(connection, agent):
    created = [
        invoice_service.create_invoice(connection, agent, _new_invoice()).id for _ in range(3)
    ]

    first = invoice_service.list_invoices(connection, agent, limit=2)
    second = invoice_service.list_invoices(connection, agent, limit=2, cursor=first.next_cursor)

    assert len(first.invoices) == 2
    assert first.next_cursor is not None
    assert len(second.invoices) == 1
    assert second.next_cursor is None
    assert {row.id for row in first.invoices + second.invoices} == set(created)


def test_invoice_page_rejects_a_corrupt_cursor(connection, agent):
    with pytest.raises(invoice_service.InvalidCursor):
        invoice_service.list_invoices(connection, agent, cursor="not-base64!!")


def test_ledger_entries_balance():
    entries = capture_entries("inv_1", 5_000, payment_id="pay_1")
    entries += refund_entries("inv_1", 5_000, payment_id="ref_1")

    assert balance_cents(entries) == 0
