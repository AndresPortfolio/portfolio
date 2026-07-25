"""In-memory tenant directory with plan + feature gates."""

from __future__ import annotations

from dataclasses import dataclass


class TenantError(Exception):
    """Raised when a user is unmapped or lacks a feature."""


@dataclass(frozen=True)
class Tenant:
    tenant_id: str
    display_name: str
    plan: str
    features: frozenset[str]
    owner_user_id: int
    seat_limit: int


_TENANTS: tuple[Tenant, ...] = (
    Tenant(
        tenant_id="acme",
        display_name="Acme Ops",
        plan="pro",
        features=frozenset({"status", "digests", "exports"}),
        owner_user_id=1001,
        seat_limit=10,
    ),
    Tenant(
        tenant_id="northwind",
        display_name="Northwind",
        plan="starter",
        features=frozenset({"status"}),
        owner_user_id=1002,
        seat_limit=3,
    ),
)

_BY_USER = {t.owner_user_id: t for t in _TENANTS}
_BY_ID = {t.tenant_id: t for t in _TENANTS}

PLAN_RANK = {"starter": 1, "pro": 2, "enterprise": 3}


def resolve_tenant(messaging_user_id: int | None) -> Tenant | None:
    if messaging_user_id is None:
        return None
    return _BY_USER.get(messaging_user_id)


def require_tenant(messaging_user_id: int | None) -> Tenant:
    tenant = resolve_tenant(messaging_user_id)
    if tenant is None:
        raise TenantError("unmapped user")
    return tenant


def require_feature(tenant: Tenant, feature: str) -> None:
    if feature not in tenant.features:
        raise TenantError(f"feature '{feature}' not enabled on plan={tenant.plan}")


def require_plan_at_least(tenant: Tenant, minimum: str) -> None:
    if PLAN_RANK.get(tenant.plan, 0) < PLAN_RANK.get(minimum, 99):
        raise TenantError(f"plan {tenant.plan} < required {minimum}")


def get_tenant(tenant_id: str) -> Tenant | None:
    return _BY_ID.get(tenant_id)
