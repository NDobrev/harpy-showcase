"""Refund eligibility rules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

REFUND_WINDOW_DAYS = 90


@dataclass(frozen=True)
class RefundRequest:
    invoice_id: str
    amount_cents: int
    reason: str


class RefundRejected(ValueError):
    """Raised when a refund is not allowed."""


def refundable_cents(captured_cents: int, refunded_cents: int) -> int:
    return max(captured_cents - refunded_cents, 0)


def check_refund(
    request: RefundRequest,
    *,
    captured_cents: int,
    refunded_cents: int,
    captured_on: date,
    today: date,
) -> int:
    if request.amount_cents <= 0:
        raise RefundRejected("refund amount must be positive")
    if captured_on + timedelta(days=REFUND_WINDOW_DAYS) < today:
        raise RefundRejected(f"invoice is outside the {REFUND_WINDOW_DAYS} day refund window")
    available = refundable_cents(captured_cents, refunded_cents)
    if request.amount_cents > available:
        raise RefundRejected(f"only {available} cents are refundable on this invoice")
    return request.amount_cents
