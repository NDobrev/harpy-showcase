"""Invoice endpoints."""

from __future__ import annotations

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from ledgerline.api.deps import get_connection, get_principal
from ledgerline.api.schemas import InvoiceIn, InvoiceOut
from ledgerline.auth.permissions import PermissionDenied, Principal
from ledgerline.domain.pricing import LineItem, PricingError
from ledgerline.services import invoice_service
from ledgerline.services.invoice_service import InvoiceNotFound, NewInvoice

router = APIRouter(tags=["invoices"])


@router.post("/v1/invoices", response_model=InvoiceOut, status_code=201)
def create_invoice(
    body: InvoiceIn,
    connection: sqlite3.Connection = Depends(get_connection),
    principal: Principal = Depends(get_principal),
) -> InvoiceOut:
    request = NewInvoice(
        customer_email=body.customer_email,
        region=body.region,
        items=[
            LineItem(item.description, item.quantity, item.unit_amount_cents) for item in body.items
        ],
        discount_percent=body.discount_percent,
    )
    try:
        invoice = invoice_service.create_invoice(connection, principal, request)
    except PermissionDenied as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except PricingError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return InvoiceOut(**vars(invoice))


@router.get("/v1/invoices/list", response_model=list[InvoiceOut])
def list_invoices(
    connection: sqlite3.Connection = Depends(get_connection),
    principal: Principal = Depends(get_principal),
) -> list[InvoiceOut]:
    try:
        rows = invoice_service.list_invoices(connection, principal)
    except PermissionDenied as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    return [InvoiceOut(**vars(row)) for row in rows]


@router.get("/v1/invoices/{invoice_id}", response_model=InvoiceOut)
def get_invoice(
    invoice_id: str,
    connection: sqlite3.Connection = Depends(get_connection),
    principal: Principal = Depends(get_principal),
) -> InvoiceOut:
    try:
        invoice, _items = invoice_service.get_invoice(connection, principal, invoice_id)
    except PermissionDenied as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except InvoiceNotFound as error:
        raise HTTPException(status_code=404, detail="invoice not found") from error
    return InvoiceOut(**vars(invoice))
