# Tiered LLM router

## What this demonstrates

- Fast model first, escalate to a deeper model on low confidence / hard prompts
- Keyword + length escalation rules
- Retries around flaky HTTP backends
- Routing transcript log for debugging agent behaviour

Offline stubs by default. Optional live OpenAI-compatible HTTP client via env vars.

## How to run

```bash
cd examples/tiered-llm-router

python router.py "restart the billing worker"
python router.py --long --transcript /tmp/route.json

# optional live endpoint
export LLM_API_KEY=...
export LLM_BASE_URL=...   # provider /v1 base URL
python router.py --live "summarize pod restarts"
```

Stdlib only for the offline path.
