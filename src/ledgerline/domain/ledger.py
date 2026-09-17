"""Double-entry ledger entries for captured and refunded money.

Every captured or refunded amount produces two entries whose debits and credits
cancel out, so `balance_cents` over a complete set is always zero.
"""

from __future__ import annotations

from dataclasses import dataclass

ACCOUNTS_RECEIVABLE = "accounts_receivable"
CASH = "cash"
REFUNDS = "refunds"


@dataclass(frozen=True)
class LedgerEntry:
    """One side of a double-entry pair."""

    invoice_id: str
    account: str
    debit_cents: int
    credit_cents: int
    memo: str


def balance_cents(entries: list[LedgerEntry]) -> int:
    """Debits minus credits. Zero for a balanced set of entries."""
    return sum(entry.debit_cents - entry.credit_cents for entry in entries)


def capture_entries(invoice_id: str, amount_cents: int, *, payment_id: str) -> list[LedgerEntry]:
    """Money in: cash is debited, receivables are credited."""
    memo = f"capture {payment_id}"
    return [
        LedgerEntry(invoice_id, CASH, amount_cents, 0, memo),
        LedgerEntry(invoice_id, ACCOUNTS_RECEIVABLE, 0, amount_cents, memo),
    ]


def refund_entries(invoice_id: str, amount_cents: int, *, payment_id: str) -> list[LedgerEntry]:
    """Money out: refunds are debited, cash is credited."""
    memo = f"refund {payment_id}"
    return [
        LedgerEntry(invoice_id, REFUNDS, amount_cents, 0, memo),
        LedgerEntry(invoice_id, CASH, 0, amount_cents, memo),
    ]
