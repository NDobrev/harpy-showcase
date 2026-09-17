"""Invoice pricing rules.

All money is an integer number of minor units (cents). Percentages are floats
between 0 and 100.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

TAX_RATES: dict[str, str] = {
    "US-CA": "0.0875",
    "US-NY": "0.08875",
    "DE": "0.19",
    "BG": "0.20",
    "XX": "0",
}

MAX_DISCOUNT_PERCENT = 40.0


@dataclass(frozen=True)
class LineItem:
    description: str
    quantity: int
    unit_amount_cents: int

    @property
    def amount_cents(self) -> int:
        return self.quantity * self.unit_amount_cents


@dataclass(frozen=True)
class InvoiceTotals:
    subtotal_cents: int
    discount_cents: int
    tax_cents: int
    total_cents: int


class PricingError(ValueError):
    """Raised when an invoice cannot be priced."""


def tax_rate_for(region: str) -> Decimal:
    if region not in TAX_RATES:
        raise PricingError(f"unknown tax region: {region}")
    return Decimal(TAX_RATES[region])


def subtotal_cents(items: list[LineItem]) -> int:
    if not items:
        raise PricingError("an invoice needs at least one line item")
    for item in items:
        if item.quantity <= 0:
            raise PricingError(f"line item {item.description!r} has a non-positive quantity")
        if item.unit_amount_cents < 0:
            raise PricingError(f"line item {item.description!r} has a negative unit amount")
    return sum(item.amount_cents for item in items)


def discount_cents(subtotal: int, discount_percent: float) -> int:
    if discount_percent < 0:
        raise PricingError("discount percent cannot be negative")
    if discount_percent > MAX_DISCOUNT_PERCENT:
        raise PricingError(f"discount percent above {MAX_DISCOUNT_PERCENT} needs approval")
    raw = Decimal(subtotal) * Decimal(str(discount_percent)) / Decimal(100)
    return int(raw.quantize(Decimal(1), rounding=ROUND_HALF_UP))


def tax_cents(subtotal: int, region: str) -> int:
    raw = Decimal(subtotal) * tax_rate_for(region)
    return int(raw.quantize(Decimal(1), rounding=ROUND_HALF_UP))


def price_invoice(
    items: list[LineItem],
    *,
    region: str,
    discount_percent: float = 0.0,
) -> InvoiceTotals:
    """Price an invoice.

    Tax is charged on the undiscounted subtotal; the discount reduces only the
    amount the customer owes.
    """
    subtotal = subtotal_cents(items)
    discount = discount_cents(subtotal, discount_percent)
    tax = tax_cents(subtotal, region)
    return InvoiceTotals(
        subtotal_cents=subtotal,
        discount_cents=discount,
        tax_cents=tax,
        total_cents=subtotal - discount + tax,
    )
