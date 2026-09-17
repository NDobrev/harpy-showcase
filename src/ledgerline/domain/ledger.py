"""Double-entry ledger entries for captured and refunded money."""

from __future__ import annotations

from dataclasses import dataclass

ACCOUNTS_RECEIVABLE = "accounts_receivable"
CASH = "cash"
REFUNDS = "refunds"


@dataclass(frozen=True)
class LedgerEntry:
    invoice_id: str
    account: str
    debit_cents: int
    credit_cents: int
    memo: str


def capture_entries(invoice_id: str, amount_cents: int, *, payment_id: str) -> list[LedgerEntry]:
    memo = f"capture {payment_id}"
    return [
        LedgerEntry(invoice_id, CASH, amount_cents, 0, memo),
        LedgerEntry(invoice_id, ACCOUNTS_RECEIVABLE, 0, amount_cents, memo),
    ]


def refund_entries(invoice_id: str, amount_cents: int, *, payment_id: str) -> list[LedgerEntry]:
    memo = f"refund {payment_id}"
    return [
        LedgerEntry(invoice_id, REFUNDS, amount_cents, 0, memo),
        LedgerEntry(invoice_id, CASH, 0, amount_cents, memo),
    ]


def balance_cents(entries: list[LedgerEntry]) -> int:
    return sum(entry.debit_cents - entry.credit_cents for entry in entries)
