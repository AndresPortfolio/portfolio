# Creator marketplace platform

## Problem

Creators needed a web surface for discovery/matching and account connection workflows — not only chat commands. Chat is great for ops; browsers are better for onboarding, dashboards, and richer UI.

## What I built

A creator SaaS web + API stack:

- Creator-facing web UI for marketplace / matching flows  
- Backend API for auth’d sessions, onboarding, and product actions  
- Connectors that attach authenticated platform sessions to a creator profile (tenant-scoped)  
- Supporting migrations as the product moved through phases  

## Architecture (high level)

```
Web UI  ──►  API service  ──►  Postgres / managed auth+data layer
                 │
                 ├── Onboarding & profile state
                 ├── Matching / marketplace actions
                 └── Session connector workflows (per creator)
```

The important boundary: **creator identity and connector state are isolated**. Cross-tenant leakage is treated as a hard failure mode, not an edge case.

## Decisions that mattered

- **Web + bot as complementary surfaces** — bots for daily ops, web for setup and marketplace UX.  
- **Phased migrations** — ship vertical slices; migrate schema deliberately instead of big-bang rewrites.  
- **Session connectors behind the API** — keep sensitive auth material off the frontend and out of logs.  
- **Lightweight frontend where speed mattered** — ship operator-usable UI without overbuilding a design system.

## Stack

Python API · HTML/JS frontend · Postgres · migrations · process-supervised API + web serving

## Skills demonstrated

Full-stack creator SaaS · tenant-safe connectors · product onboarding design · pragmatic UI/API split · iterative schema delivery
