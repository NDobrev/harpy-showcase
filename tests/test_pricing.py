from __future__ import annotations

import pytest

from ledgerline.domain.pricing import (
    LineItem,
    PricingError,
    discount_cents,
    price_invoice,
    subtotal_cents,
    tax_cents,
)

SEAT = LineItem("Team seat", 3, 1_999)
SUPPORT = LineItem("Priority support", 1, 4_900)


def test_subtotal_sums_line_amounts():
    assert subtotal_cents([SEAT, SUPPORT]) == 10_897


def test_subtotal_rejects_empty_invoice():
    with pytest.raises(PricingError):
        subtotal_cents([])


def test_subtotal_rejects_non_positive_quantity():
    with pytest.raises(PricingError):
        subtotal_cents([LineItem("Bad", 0, 100)])


def test_tax_rounds_half_up():
    assert tax_cents(10_897, "US-CA") == 953


def test_tax_rejects_unknown_region():
    with pytest.raises(PricingError):
        tax_cents(1_000, "MARS")


def test_discount_above_ceiling_is_rejected():
    with pytest.raises(PricingError):
        discount_cents(10_000, 55.0)


def test_tax_is_charged_on_the_undiscounted_subtotal():
    totals = price_invoice([SEAT, SUPPORT], region="US-CA", discount_percent=10.0)

    assert totals.subtotal_cents == 10_897
    assert totals.discount_cents == 1_090
    assert totals.tax_cents == 953
    assert totals.total_cents == 10_760
