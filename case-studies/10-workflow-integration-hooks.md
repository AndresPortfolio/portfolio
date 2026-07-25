# Workflow integration hooks

## Problem

Ops often spans multiple external platforms. I needed thin, reliable hooks for ingest and scheduling — not a monolith that pretends every integration is the same.

## What I built

Smaller services focused on:

- Ingest hooks that accept content/events from upstream tools
- Platform-specific publishers / schedulers
- Clear failure isolation so one integration can’t take down the core SaaS

## Architecture (high level)

```
Upstream content / ops tools
            │
            ▼
     Ingest hooks (per channel)
            │
     ┌──────┴──────┐
     ▼             ▼
 Scheduler A    Scheduler B
 (platform)     (platform)
```

Each integration is its own supervised unit with its own logs and restart domain.

## Decisions that mattered

- **Prefer many small services** — external APIs and auth models diverge; isolation beats clever abstraction.
- **Ingest as a contract** — normalize early, publish late.
- **Fail closed per platform** — a broken publisher shouldn’t corrupt tenant state in the core product.
- **Operate them like products** — health labels, restart policy, and docs registry entries for each hook.

## Stack

Python / Node services · messaging or HTTP ingest · platform SDKs or browser automation where required · process supervision

## Skills demonstrated

Integration architecture · blast-radius control · platform adapter thinking · fleet-friendly service design
