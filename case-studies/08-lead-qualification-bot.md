# Lead qualification bot

## Problem

Inbound interest in a Telegram business channel mixed tire-kickers with real buyers. I needed structured qualification, persistent lead storage, and alerts when someone was hot — without a full CRM.

## What I built

A sales funnel bot that:

- Runs qualification conversations  
- Stores leads in SQLite  
- Flags hot leads to an operator inbox  
- Stays simple enough to run as a supervised long-lived service  

## Architecture (high level)

```
Prospect (Telegram)
      │
      ▼
Sales bot (conversation state)
      │
      ├── Qualification script / branches
      ├── Lead persistence (SQLite)
      └── Hot-lead alert → operator
```

## Decisions that mattered

- **SQLite is enough** — early funnel volume doesn’t need a distributed DB; durability and simplicity win.  
- **Hot-lead alerts beat dashboards** — operators respond to pings, not empty analytics pages.  
- **Business-chat native** — meet prospects where they already are.  
- **Keep the script editable** — qualification criteria change; don’t bury them in unreachable code.

## Stack

Python · python-telegram-bot · SQLite · dotenv-based config · launchd-style supervision

## Skills demonstrated

Conversational funnels · lightweight CRM patterns · alert-driven ops · shipping revenue tooling fast
