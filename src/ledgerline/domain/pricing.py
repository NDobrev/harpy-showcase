"""Invoice pricing rules.

All money is an integer number of minor units (cents). Percentages are floats
between 0 and 100.

A discount is spread across the line items it applies to, and tax is charged on
what the customer actually owes for each line.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal

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
class LinePrice:
    description: str
    amount_cents: int
    discount_cents: int
    tax_cents: int

    @property
    def taxable_cents(self) -> int:
        return self.amount_cents - self.discount_cents

    @property
    def total_cents(self) -> int:
        return self.taxable_cents + self.tax_cents


@dataclass(frozen=True)
class InvoiceTotals:
    subtotal_cents: int
    discount_cents: int
    tax_cents: int
    total_cents: int
    lines: tuple[LinePrice, ...] = ()


class PricingError(ValueError):
    """Raised when an invoice cannot be priced."""


def _to_cents(value: Decimal) -> int:
    """Round to whole cents, half to even, so repeated pricing does not drift up."""
    return int(value.quantize(Decimal(1), rounding=ROUND_HALF_EVEN))


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
    return _to_cents(raw)


def tax_cents(subtotal: int, region: str) -> int:
    return _to_cents(Decimal(subtotal) * tax_rate_for(region))


def allocate_discount(items: list[LineItem], total_discount: int) -> list[int]:
    """Split `total_discount` across `items` in proportion to their amounts.

    Uses the largest remainder method: every line gets its floored share, then
    the leftover cents go to the lines with the largest fractional part. The
    returned amounts always sum to `total_discount` exactly.
    """
    subtotal = sum(item.amount_cents for item in items)
    if total_discount == 0 or subtotal == 0:
        return [0] * len(items)
    shares = [Decimal(item.amount_cents) * total_discount / Decimal(subtotal) for item in items]
    allocated = [int(share) for share in shares]
    leftover = total_discount - sum(allocated)
    ranked = sorted(
        range(len(items)),
        key=lambda index: (shares[index] - allocated[index], items[index].amount_cents),
        reverse=True,
    )
    for index in ranked[:leftover]:
        allocated[index] += 1
    return allocated


def price_invoice(
    items: list[LineItem],
    *,
    region: str,
    discount_percent: float = 0.0,
) -> InvoiceTotals:
    """Price an invoice.

    The discount is prorated across the line items, and each line is taxed on
    its discounted amount, so a discount reduces the tax the customer owes.
    """
    subtotal = subtotal_cents(items)
    discount = discount_cents(subtotal, discount_percent)
    rate = tax_rate_for(region)
    allocations = allocate_discount(items, discount)
    lines = tuple(
        LinePrice(
            description=item.description,
            amount_cents=item.amount_cents,
            discount_cents=line_discount,
            tax_cents=_to_cents(Decimal(item.amount_cents - line_discount) * rate),
        )
        for item, line_discount in zip(items, allocations, strict=True)
    )
    tax = sum(line.tax_cents for line in lines)
    return InvoiceTotals(
        subtotal_cents=subtotal,
        discount_cents=discount,
        tax_cents=tax,
        total_cents=subtotal - discount + tax,
        lines=lines,
    )
