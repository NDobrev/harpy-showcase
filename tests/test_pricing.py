from __future__ import annotations

import pytest

from ledgerline.domain.pricing import (
    LineItem,
    PricingError,
    allocate_discount,
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


def test_tax_rounds_half_to_even():
    assert tax_cents(10_897, "US-CA") == 953
    assert tax_cents(1_050, "US-CA") == 92  # 91.875 → 92
    assert tax_cents(200, "BG") == 40


def test_tax_rejects_unknown_region():
    with pytest.raises(PricingError):
        tax_cents(1_000, "MARS")


def test_discount_above_ceiling_is_rejected():
    with pytest.raises(PricingError):
        discount_cents(10_000, 55.0)


def test_discount_is_prorated_and_sums_exactly():
    allocations = allocate_discount([SEAT, SUPPORT], 1_090)

    assert sum(allocations) == 1_090
    assert allocations == [600, 490]  # leftover cent goes to the larger line


def test_discount_allocation_handles_a_free_line():
    allocations = allocate_discount([SEAT, LineItem("Free trial", 1, 0)], 600)

    assert allocations == [600, 0]


def test_tax_is_charged_on_the_discounted_line_amounts():
    totals = price_invoice([SEAT, SUPPORT], region="US-CA", discount_percent=10.0)

    assert totals.subtotal_cents == 10_897
    assert totals.discount_cents == 1_090
    assert totals.tax_cents == 858
    assert totals.total_cents == 10_665


def test_line_breakdown_reconciles_with_the_invoice_totals():
    totals = price_invoice([SEAT, SUPPORT], region="DE", discount_percent=15.0)

    assert sum(line.discount_cents for line in totals.lines) == totals.discount_cents
    assert sum(line.tax_cents for line in totals.lines) == totals.tax_cents
    assert sum(line.total_cents for line in totals.lines) == totals.total_cents


def test_zero_rate_region_charges_no_tax():
    totals = price_invoice([SEAT], region="XX", discount_percent=10.0)

    assert totals.tax_cents == 0
    assert totals.total_cents == totals.subtotal_cents - totals.discount_cents
