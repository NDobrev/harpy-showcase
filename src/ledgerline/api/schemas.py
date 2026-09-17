"""Request and response bodies for the HTTP API.

Every model here is part of the public contract: renaming a field or tightening
a constraint changes what clients may send.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class LineItemIn(BaseModel):
    """One billable line on a new invoice."""

    description: str = Field(min_length=1, max_length=200)
    quantity: int = Field(ge=1)
    unit_amount_cents: int = Field(ge=0)


class InvoiceIn(BaseModel):
    """Body of `POST /v1/invoices`."""

    customer_email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    region: str
    items: list[LineItemIn] = Field(min_length=1)
    discount_percent: float = Field(default=0.0, ge=0)


class InvoiceOut(BaseModel):
    """An invoice with its priced totals."""

    id: str
    customer_email: str
    region: str
    status: str
    subtotal_cents: int
    discount_cents: int
    tax_cents: int
    total_cents: int
    created_at: str


class CaptureIn(BaseModel):
    """Body of `POST /v1/invoices/{invoice_id}/captures`."""

    amount_cents: int = Field(gt=0)


class PaymentOut(BaseModel):
    """A capture or a refund."""

    id: str
    invoice_id: str
    kind: str
    amount_cents: int
    created_at: str


class ErrorOut(BaseModel):
    """Error envelope."""

    error: str
    detail: str
