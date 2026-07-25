# Autonomous ops agent

## Problem

I was the on-call rotation. Repeating “check health → read logs → restart → confirm” across many services burns hours. I needed a conversational agent that can diagnose and act — with a safe escalation path when code changes are required.

## What I built

A messaging-facing ops agent that:

- Pins / refreshes an operational board (status-style digests)
- Accepts free-text ops questions
- Inspects services, queries local state, reads logs
- Restarts known services within policy
- Escalates harder fixes to a coding agent workflow when needed

## Architecture (high level)

```
Operator (chat)
      │
      ▼
Ops agent runtime
      │
      ├── Fast LLM tier (routine replies)
      ├── Deep LLM tier (harder reasoning)
      ├── Ops API client (metrics / board)
      ├── Local inspectors (services, logs, DBs)
      └── Escalation bridge (code-change workflows)
```

## Decisions that mattered

- **Tiered models** — cheap/fast for chatter; stronger model only when the fast path stalls.
- **Allowlisted actions** — restarts and inspections are policy-bound; not a raw shell for anyone who messages the bot.
- **Escalation, not ego** — when the right move is a code fix, hand off instead of hallucinating patches in chat.
- **Replace, don’t duplicate** — one conversational ops bot as the daily driver; keep metrics APIs underneath.

## Stack

Python · messaging bot framework · LLM routing via OpenAI-compatible APIs · local service control · optional coding-agent SDK integration

## Skills demonstrated

Agent design · tool-using LLMs · safe automation boundaries · ops productization · escalation architecture
