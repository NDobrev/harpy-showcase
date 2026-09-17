"""Request and response bodies for the HTTP API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LineItemIn(BaseModel):
    description: str = Field(min_length=1, max_length=200)
    quantity: int = Field(ge=1)
    unit_amount_cents: int = Field(ge=0)


class InvoiceIn(BaseModel):
    customer_email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    region: str
    items: list[LineItemIn] = Field(min_length=1)
    discount_percent: float = Field(default=0.0, ge=0)


class InvoiceOut(BaseModel):
    id: str
    customer_email: str
    region: str
    status: str
    subtotal_cents: int
    discount_cents: int
    tax_cents: int
    total_cents: int
    created_at: str


class InvoicePageOut(BaseModel):
    data: list[InvoiceOut]
    next_cursor: str | None = None


class CaptureIn(BaseModel):
    amount_cents: int = Field(gt=0)


class RefundIn(BaseModel):
    amount_cents: int = Field(gt=0)
    reason: str = Field(min_length=1, max_length=200)


class PaymentOut(BaseModel):
    id: str
    invoice_id: str
    kind: str
    amount_cents: int
    created_at: str


class ErrorOut(BaseModel):
    error: str
    detail: str
