# Andres Portfolio

Architecture writeups from production systems I’ve designed, built, and operated as a solo founder-engineer.

Focus areas: **creator SaaS**, **multi-tenant platforms**, **Telegram product surfaces**, **ops automation**, and **AI-assisted tooling**.

Writeups describe *what* was built and *how it was shaped*. The `examples/` folder has small, runnable skeletons that show the patterns — not proprietary production source, credentials, infrastructure addresses, or client data.

---

## Skills

| Area | What I actually ship |
|------|----------------------|
| **Backend** | Python services, async APIs, SQLAlchemy, Postgres + SQLite, Alembic migrations |
| **Bots & messaging** | Multi-tenant Telegram products (handlers, billing flows, partner portals, digests) |
| **Web** | Lightweight frontends + API backends for creator-facing workflows |
| **Data** | Tenant isolation, lead funnels, operational metrics, health registries |
| **Automation** | Scheduled jobs, browser automation, process supervision on macOS (`launchd`) |
| **AI** | LLM-backed ops agents, caption/generation pipelines, tiered model routing |
| **Ops** | Fleet monitoring, restart/recovery, watchdog patterns, human-in-the-loop escalation |
| **Product** | Turning messy operator work into paid multi-tenant SaaS |

---

## Case studies

1. [Multi-tenant Telegram SaaS](case-studies/01-multi-tenant-telegram-saas.md) — billing, partners, channel ops at tenant scale  
2. [Creator marketplace platform](case-studies/02-creator-marketplace-platform.md) — web + API for matching and onboarding  
3. [Fleet ops dashboard](case-studies/03-fleet-ops-dashboard.md) — monitoring, health, Notion-synced ops surface  
4. [Autonomous ops agent](case-studies/04-autonomous-ops-agent.md) — conversational diagnosis, restarts, escalation  
5. [Content scheduling system](case-studies/05-content-scheduling-system.md) — queues, delays, browser-driven publishing  
6. [Media processing pipeline](case-studies/06-media-processing-pipeline.md) — batch transforms for uniqueness / distribution  
7. [AI caption lab](case-studies/07-ai-caption-lab.md) — experiment loops around LLM caption generation  
8. [Lead qualification bot](case-studies/08-lead-qualification-bot.md) — sales funnel, SQLite leads, hot-lead alerts  
9. [Candidate screening bot](case-studies/09-candidate-screening-bot.md) — structured intake and digest reporting  
10. [Social publishing hooks](case-studies/10-social-publishing-hooks.md) — ingest + schedule patterns for social platforms  

---

## Code examples

Sanitized, runnable sketches — safe to clone and poke at:

| Example | What it demonstrates |
|---------|----------------------|
| [telegram-tenant-bot](examples/telegram-tenant-bot/) | Multi-tenant Telegram bot: user→tenant resolution, allowlisted admin commands, `/health` for supervisors |
| [health-board](examples/health-board/) | Tiny fleet status probe — one-line board + non-zero exit when something is down |

---

## How to read this

Each writeup covers:

- **Problem** — the operational pain that justified building  
- **Architecture** — components and boundaries (high level)  
- **Decisions** — trade-offs that mattered in production  
- **Skills demonstrated** — concrete engineering signals  

Intentionally omitted: production source, real secrets, hostnames, IPs, domains, client identities, and anything NSFW or platform-restricted.

See [OMISSIONS.md](OMISSIONS.md).

---

## About

I’m Andres — solo builder shipping real multi-tenant creator SaaS and the ops layer required to keep it alive. This portfolio is the public, sanitized view of that work.
