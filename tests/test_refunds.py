from __future__ import annotations

from datetime import date

import pytest

from ledgerline.domain.refunds import RefundRejected, RefundRequest, check_refund

CAPTURED_ON = date(2026, 1, 10)


def test_refund_within_window_and_balance_is_allowed():
    request = RefundRequest("inv_1", 5_000, "duplicate charge")

    amount = check_refund(
        request,
        captured_cents=10_000,
        refunded_cents=0,
        captured_on=CAPTURED_ON,
        today=date(2026, 2, 1),
    )

    assert amount == 5_000


def test_refund_above_remaining_balance_is_rejected():
    request = RefundRequest("inv_1", 6_000, "duplicate charge")

    with pytest.raises(RefundRejected):
        check_refund(
            request,
            captured_cents=10_000,
            refunded_cents=5_000,
            captured_on=CAPTURED_ON,
            today=date(2026, 2, 1),
        )


def test_refund_outside_window_is_rejected():
    request = RefundRequest("inv_1", 1_000, "late")

    with pytest.raises(RefundRejected):
        check_refund(
            request,
            captured_cents=10_000,
            refunded_cents=0,
            captured_on=CAPTURED_ON,
            today=date(2026, 6, 1),
        )
