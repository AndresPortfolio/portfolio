# Multi-tenant Telegram SaaS

## Problem

Operators managing many creators needed one product surface for channel workflows, partner coordination, and billing — without spinning up a bespoke bot per tenant.

## What I built

A production Telegram SaaS where each customer (tenant) gets isolated configuration, data, and workflows inside a shared bot runtime.

Core capabilities:

- Tenant onboarding and configuration  
- Channel / content-ops workflows inside Telegram  
- Partner portal flows for collaboration  
- Billing and entitlement gating  
- Background health / watchdog processes so the product stays up  

## Architecture (high level)

```
Telegram clients
      │
      ▼
Bot runtime (handler layers)
      │
      ├── Tenant context resolution
      ├── Feature handlers (ops / partners / billing)
      └── Background workers (scheduler, monitor, health)
      │
      ▼
Postgres (primary) + SQLite where local durability helps
```

Process supervision runs as long-lived services with dedicated health checks and recovery helpers — important when the bot *is* the product.

## Decisions that mattered

- **Shared runtime, hard tenant boundaries** — one deploy, many customers; isolation is a data/model concern, not “one process per client.”  
- **Postgres for multi-tenant truth** — relational model + migrations for billing/partner state that must survive restarts.  
- **Watchdogs as first-class** — messaging products fail quietly; monitoring and auto-recovery are product features.  
- **Partner flows in-product** — reduces spreadsheet ops and keeps collaboration inside the paid surface.

## Stack

Python · python-telegram-bot / Telethon · SQLAlchemy · asyncpg · Alembic · APScheduler · Playwright · structured logging

## Skills demonstrated

Multi-tenant product design · async bot architecture · billing-aware feature gates · operational hardening · schema evolution under live tenants
