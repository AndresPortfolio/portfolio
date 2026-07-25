# Tiered LLM router

Fast model first, escalate to a deeper model on low confidence / hard prompts.
Retries + transcript log included.

```bash
cd examples/tiered-llm-router

# offline stubs (no keys)
python router.py "restart the billing worker"
python router.py --long --transcript /tmp/route.json

# optional live OpenAI-compatible endpoint
export LLM_API_KEY=...
export LLM_BASE_URL=...   # e.g. your provider's /v1 base URL
python router.py --live "summarize pod restarts"
```

Stdlib only for the offline path.
