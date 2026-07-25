# Andre Naidoo — Engineering Portfolio

Architecture writeups from production systems I've designed, built, and operated as a solo founder-engineer.

Focus areas: **multi-tenant SaaS platforms**, **messaging-based product surfaces**, **ops automation**, and **AI-assisted tooling**.

Writeups describe *what* was built and *how it was shaped*. The `examples/` folder has small, runnable skeletons that show the patterns — not proprietary source, credentials, infrastructure addresses, or client data.

---

## Skills

| Area | What I actually ship |
|------|----------------------|
| **Backend** | Python services, async APIs, SQLAlchemy, Postgres + SQLite, Alembic migrations |
| **Bots & messaging** | Multi-tenant messaging-platform products (handlers, billing flows, partner portals, digests) |
| **Web** | Lightweight frontends + API backends for B2B workflows |
| **Data** | Tenant isolation, funnel tracking, operational metrics, health registries |
| **Automation** | Scheduled jobs, browser automation, process supervision on macOS (`launchd`) |
| **AI** | LLM-backed ops agents, text-generation pipelines, tiered model routing |
| **Ops** | Fleet monitoring, restart/recovery, watchdog patterns, human-in-the-loop escalation |
| **Product** | Turning operational workflows into paid multi-tenant SaaS |

---

## Case studies

1. [Multi-tenant messaging platform](case-studies/01-multi-tenant-messaging-platform.md) — billing, partner management, workspace ops at tenant scale
2. [B2B marketplace platform](case-studies/02-b2b-marketplace-platform.md) — web + API for matching and onboarding
3. [Fleet ops dashboard](case-studies/03-fleet-ops-dashboard.md) — monitoring, health, synced ops surface
4. [Autonomous ops agent](case-studies/04-autonomous-ops-agent.md) — conversational diagnosis, restarts, escalation
5. [Automated scheduling system](case-studies/05-automated-scheduling-system.md) — queues, delays, browser-driven publishing
6. [Media processing pipeline](case-studies/06-media-processing-pipeline.md) — batch transforms at scale
7. [AI text-generation lab](case-studies/07-ai-text-generation-lab.md) — experiment loops around LLM-based content generation
8. [Lead qualification bot](case-studies/08-lead-qualification-bot.md) — sales funnel, structured intake, hot-lead alerts
9. [Candidate screening bot](case-studies/09-candidate-screening-bot.md) — structured intake and digest reporting
10. [Workflow integration hooks](case-studies/10-workflow-integration-hooks.md) — ingest + schedule patterns for external platforms

---

## Code examples

Sanitized, runnable sketches — safe to clone and poke at:

| Example | What it demonstrates |
|---------|----------------------|
| [messaging-tenant-bot](examples/messaging-tenant-bot/) | Multi-tenant messaging bot: user→tenant resolution, allowlisted admin commands, `/health` for supervisors |
| [health-board](examples/health-board/) | Tiny fleet status probe — one-line board + non-zero exit when something is down |

---

## How to read this

Each writeup covers:

- **Problem** — the operational pain that justified building
- **Architecture** — components and boundaries (high level)
- **Decisions** — trade-offs that mattered in production
- **Skills demonstrated** — concrete engineering signals

Intentionally omitted: production source, real secrets, hostnames, IPs, domains, client identities.

See [OMISSIONS.md](OMISSIONS.md).

---

## About

I'm Andre — solo builder shipping production multi-tenant SaaS products and the ops layer required to keep them running. This portfolio is the public, sanitized view of that work.
