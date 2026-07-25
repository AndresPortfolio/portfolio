"""In-memory tenant directory — swap for Postgres in a real product."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Tenant:
    tenant_id: str
    display_name: str
    plan: str
    features: tuple[str, ...]
    owner_user_id: int


# Demo data only. In production this is a DB lookup keyed by messaging user id.
_TENANTS: tuple[Tenant, ...] = (
    Tenant(
        tenant_id="acme",
        display_name="Acme Ops",
        plan="pro",
        features=("status", "digests"),
        owner_user_id=1001,
    ),
    Tenant(
        tenant_id="northwind",
        display_name="Northwind",
        plan="starter",
        features=("status",),
        owner_user_id=1002,
    ),
)

_BY_USER = {t.owner_user_id: t for t in _TENANTS}


def resolve_tenant(messaging_user_id: int | None) -> Tenant | None:
    """Map a messaging user to exactly one tenant, or None if unmapped."""
    if messaging_user_id is None:
        return None
    return _BY_USER.get(messaging_user_id)
