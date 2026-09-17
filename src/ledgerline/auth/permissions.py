"""Role based permissions.

`agent` handles day to day invoicing; refunds above the agent ceiling are an
`admin` decision.
"""

from __future__ import annotations

from dataclasses import dataclass

INVOICE_READ = "invoice:read"
INVOICE_WRITE = "invoice:write"
PAYMENT_CAPTURE = "payment:capture"
REFUND_ISSUE = "refund:issue"

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "viewer": frozenset({INVOICE_READ}),
    "agent": frozenset({INVOICE_READ, INVOICE_WRITE, PAYMENT_CAPTURE}),
    "admin": frozenset({INVOICE_READ, INVOICE_WRITE, PAYMENT_CAPTURE, REFUND_ISSUE}),
}

AGENT_REFUND_CEILING_CENTS = 25_000


@dataclass(frozen=True)
class Principal:
    user_id: str
    role: str

    @property
    def permissions(self) -> frozenset[str]:
        return ROLE_PERMISSIONS.get(self.role, frozenset())


class PermissionDenied(PermissionError):
    """Raised when a principal may not perform an action."""


def can(principal: Principal, permission: str) -> bool:
    return permission in principal.permissions


def authorize(principal: Principal, permission: str) -> None:
    if not can(principal, permission):
        raise PermissionDenied(f"role {principal.role!r} may not {permission}")


def authorize_refund(principal: Principal, amount_cents: int) -> None:
    authorize(principal, REFUND_ISSUE)
    if principal.role != "admin" and amount_cents > AGENT_REFUND_CEILING_CENTS:
        raise PermissionDenied(
            f"refunds above {AGENT_REFUND_CEILING_CENTS} cents require an admin"
        )
