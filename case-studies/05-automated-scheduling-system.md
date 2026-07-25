# Automated scheduling system

## Problem

Manual publishing across accounts doesn’t scale and is error-prone. Scheduling needed queueing, delays, and browser-driven actions — without posting test material to live accounts by accident.

## What I built

A scheduler oriented around:

- Per-account queues and publish windows
- Deliberate action delays (rate / safety pacing)
- Browser automation for platforms that don’t offer a clean public API path
- Hard separation between test runs and live account targets

## Architecture (high level)

```
Schedule inputs
      │
      ▼
Scheduler service
      │
      ├── Queue + timing rules
      ├── Account session resolver
      └── Browser automation worker
      │
      ▼
Target platform (via authenticated session)
```

Account resolution goes through registries — never “remembered ports” or ad-hoc profile paths.

## Decisions that mattered

- **Safety pacing** — fixed delays between actions reduce ban risk and make failures debuggable.
- **Registry-based session lookup** — isolation bugs are worse than downtime; resolve identity before acting.
- **Live vs test discipline** — production accounts are sacred; test content never ships there.
- **Browser automation as a last mile** — when APIs are insufficient, Playwright-style control is a product necessity, not a hack.

## Stack

Python · schedulers · Playwright / browser automation · supervised workers · session registries

## Skills demonstrated

Job scheduling · browser automation · account isolation · production safety culture · operator-grade tooling
