# Candidate screening bot

## Problem

Screening applicants / chatters manually doesn’t scale. I needed structured intake, scheduled digests, and optional form-driven follow-ups — so humans review summaries, not raw chat noise.

## What I built

A Telegram screening bot with:

- Structured interview / intake flows  
- Morning/evening digest jobs  
- Optional form exports / scheduled typeform-style pushes  
- Clear admin commands for operators  

## Architecture (high level)

```
Applicant
   │
   ▼
Screening bot (state machine)
   │
   ├── Responses → local store
   ├── Digest schedulers (AM/PM)
   └── Operator summaries / exports
```

## Decisions that mattered

- **Digests over realtime spam** — batch human attention.  
- **State machine clarity** — screening flows fail when “where is this user?” is ambiguous.  
- **Multiple launchd timers** — separate concerns (bot runtime vs digest jobs vs form pushes).  
- **PDF / export paths when needed** — operators still live in documents.

## Stack

Python · python-telegram-bot · scheduled jobs · structured logging · local persistence

## Skills demonstrated

Intake bots · scheduled reporting · operator UX · splitting runtime vs cron-like responsibilities
