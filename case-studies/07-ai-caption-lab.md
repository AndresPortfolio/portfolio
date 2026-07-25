# AI caption lab

## Problem

Caption writing is repetitive and quality varies. I needed an experiment surface to iterate on prompts, models, and realism — without baking every experiment into production bots.

## What I built

A lab / service layer for:

- Caption generation via LLM APIs  
- Experiment sandboxes for realism and phrasing  
- Feedback loops that promote good outputs into approved sets  
- Clear separation between research runs and production callers  

## Architecture (high level)

```
Caller (bot / script / UI)
      │
      ▼
Caption service
      │
      ├── Prompt templates
      ├── Model router
      └── Optional evaluation / realism checks
      │
      ▼
Generated captions (+ optional approval store)
```

## Decisions that mattered

- **Lab vs production** — experiments can be wrong; production callers should consume stable interfaces.  
- **Approval stores** — human taste still matters; keep a path from “generated” to “blessed.”  
- **Model flexibility** — OpenAI-compatible routing makes provider swaps boring (good).  
- **Measurable iteration** — treat caption quality as something you can A/B, not vibes-only.

## Stack

Node and/or Python services · LLM APIs · local experiment sandboxes · structured output stores

## Skills demonstrated

LLM productization · experiment hygiene · prompt/system iteration · separating R&D from production paths
