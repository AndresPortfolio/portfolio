"""
Async tenant store — SQLAlchemy 2.0 async style on SQLite.

Swap the DSN to Postgres in production (`postgresql+asyncpg://...`).
Demonstrates tenant-scoped queries and a simple entitlement check.
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from sqlalchemy import Boolean, ForeignKey, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

DB_PATH = Path(__file__).with_name("tenants.db")
DSN = f"sqlite+aiosqlite:///{DB_PATH}"


class Base(DeclarativeBase):
    pass


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    plan: Mapped[str] = mapped_column(String(32), default="starter")
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    users: Mapped[list["TenantUser"]] = relationship(back_populates="tenant")


class TenantUser(Base):
    __tablename__ = "tenant_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    external_user_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(32), default="member")

    tenant: Mapped[Tenant] = relationship(back_populates="users")


engine = create_async_engine(DSN, echo=False)
Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed() -> None:
    async with Session() as session:
        existing = await session.scalar(select(Tenant).where(Tenant.slug == "acme"))
        if existing:
            print("seed: already present")
            return
        acme = Tenant(slug="acme", plan="pro", active=True)
        north = Tenant(slug="northwind", plan="starter", active=True)
        session.add_all(
            [
                acme,
                north,
                TenantUser(tenant=acme, external_user_id="user-1001", role="owner"),
                TenantUser(tenant=north, external_user_id="user-1002", role="owner"),
                TenantUser(tenant=acme, external_user_id="user-1003", role="member"),
            ]
        )
        await session.commit()
        print("seed: inserted acme + northwind")


async def resolve(external_user_id: str) -> None:
    async with Session() as session:
        stmt = (
            select(TenantUser, Tenant)
            .join(Tenant, TenantUser.tenant_id == Tenant.id)
            .where(TenantUser.external_user_id == external_user_id)
        )
        row = (await session.execute(stmt)).first()
        if row is None:
            print(f"unmapped: {external_user_id}")
            return
        user, tenant = row
        print(
            f"user={user.external_user_id} role={user.role} "
            f"tenant={tenant.slug} plan={tenant.plan} active={tenant.active}"
        )


async def require_plan(external_user_id: str, minimum: str) -> None:
    rank = {"starter": 1, "pro": 2, "enterprise": 3}
    async with Session() as session:
        stmt = (
            select(TenantUser, Tenant)
            .join(Tenant, TenantUser.tenant_id == Tenant.id)
            .where(TenantUser.external_user_id == external_user_id)
        )
        row = (await session.execute(stmt)).first()
        if row is None:
            raise SystemExit(f"denied: unmapped {external_user_id}")
        _user, tenant = row
        if not tenant.active:
            raise SystemExit(f"denied: tenant {tenant.slug} inactive")
        if rank.get(tenant.plan, 0) < rank.get(minimum, 99):
            raise SystemExit(
                f"denied: {tenant.slug} plan={tenant.plan} < required={minimum}"
            )
        print(f"allowed: {external_user_id} on {tenant.slug} ({tenant.plan})")


async def list_members(tenant_slug: str) -> None:
    async with Session() as session:
        tenant = await session.scalar(select(Tenant).where(Tenant.slug == tenant_slug))
        if tenant is None:
            print("unknown tenant")
            return
        rows = (
            await session.execute(
                select(TenantUser).where(TenantUser.tenant_id == tenant.id)
            )
        ).scalars()
        for user in rows:
            print(f"{user.external_user_id:12} {user.role}")


async def amain() -> None:
    parser = argparse.ArgumentParser(description="Async tenant store demo")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sub.add_parser("seed")
    r = sub.add_parser("resolve")
    r.add_argument("external_user_id")
    p = sub.add_parser("require-plan")
    p.add_argument("external_user_id")
    p.add_argument("--min", default="pro")
    m = sub.add_parser("members")
    m.add_argument("tenant_slug")
    args = parser.parse_args()

    await init_db()
    if args.cmd == "init":
        print(f"ready: {DB_PATH}")
    elif args.cmd == "seed":
        await seed()
    elif args.cmd == "resolve":
        await resolve(args.external_user_id)
    elif args.cmd == "require-plan":
        await require_plan(args.external_user_id, args.min)
    elif args.cmd == "members":
        await list_members(args.tenant_slug)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(amain())
