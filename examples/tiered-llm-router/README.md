# Tiered LLM router

Shows the **fast → deep** escalation pattern used in ops agents:

1. Ask a cheap/fast model first
2. If confidence is low, escalate to a stronger model
3. Keep the interface identical so callers don’t care which tier answered

Default backends are offline stubs — no API keys needed.

```bash
cd examples/tiered-llm-router
python router.py "restart the billing worker"
python router.py --long
```

Swap `FastStub` / `DeepStub` for OpenAI-compatible clients in a real deploy.
