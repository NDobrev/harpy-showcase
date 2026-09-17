"""Payment endpoints."""

from __future__ import annotations

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from ledgerline.api.deps import get_connection, get_principal
from ledgerline.api.schemas import CaptureIn, PaymentOut
from ledgerline.auth.permissions import INVOICE_READ, PermissionDenied, Principal, authorize
from ledgerline.db.repositories import payments as payment_repo
from ledgerline.services import payment_service
from ledgerline.services.invoice_service import InvoiceNotFound

router = APIRouter(tags=["payments"])


@router.post("/v1/invoices/{invoice_id}/captures", response_model=PaymentOut, status_code=201)
def capture_payment(
    invoice_id: str,
    body: CaptureIn,
    connection: sqlite3.Connection = Depends(get_connection),
    principal: Principal = Depends(get_principal),
) -> PaymentOut:
    """Capture money against an open invoice."""
    try:
        payment = payment_service.capture_payment(
            connection, principal, invoice_id, body.amount_cents
        )
    except PermissionDenied as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except InvoiceNotFound as error:
        raise HTTPException(status_code=404, detail="invoice not found") from error
    except payment_service.CaptureRejected as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return PaymentOut(**vars(payment))


@router.get("/v1/invoices/{invoice_id}/payments", response_model=list[PaymentOut])
def list_payments(
    invoice_id: str,
    connection: sqlite3.Connection = Depends(get_connection),
    principal: Principal = Depends(get_principal),
) -> list[PaymentOut]:
    """Captures and refunds recorded for an invoice."""
    try:
        authorize(principal, INVOICE_READ)
    except PermissionDenied as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    rows = payment_repo.list_payments(connection, invoice_id)
    return [PaymentOut(**vars(row)) for row in rows]
