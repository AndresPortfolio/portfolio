# Fleet ops dashboard

## Problem

Running many bots and services solo means status lives in terminals, process lists, and chat memory. That’s fragile. I needed a single ops surface: what’s healthy, what’s degraded, what needs a human.

## What I built

An ops platform with:

- An API that aggregates fleet health and operational metrics
- A console / dashboard for day-to-day monitoring
- Sync hooks into external docs boards for status that non-terminal people can read
- Clear separation between **live status** (machine truth) and **stable registry** (paths, labels, ownership)

## Architecture (high level)

```
Supervised services (bots, APIs, workers)
            │
            ▼
     Ops API (health + metrics)
            │
     ┌──────┴──────┐
     ▼             ▼
 Ops console    External docs sync
```

Docs that describe the fleet are generated/updated from registries so agents and humans don’t invent paths from memory.

## Decisions that mattered

- **Trust process manager over stale docs** — when docs and live status disagree, live wins; then docs get fixed.
- **Stable vs live artifacts** — one file for topology, one for heartbeat-style status.
- **API as the ops contract** — other tools (agents, bots, dashboards) consume the same source of truth.
- **Human-readable sync** — status that only exists in a terminal isn’t operable when you’re away from the machine.

## Stack

Python services · local DBs for ops state · supervised long-running processes · docs sync integrations

## Skills demonstrated

Observability for small fleets · registry design · ops UX · treating infrastructure docs as generated products
