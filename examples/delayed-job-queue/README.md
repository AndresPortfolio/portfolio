# Delayed job queue

## What this demonstrates

- Delayed execution via `run_at`
- Worker leases / claim semantics
- Retry with backoff and dead-lettering after max attempts
- Simple publish/notify handlers as stand-ins for real work

SQLite-backed; no Redis/Celery required.

## How to run

```bash
cd examples/delayed-job-queue

# one-shot demo (enqueue + work)
python queue.py demo

# or step by step
python queue.py enqueue --kind publish --delay 1 --json '{"account":"acme","body":"hi"}'
python queue.py work --seconds 3
python queue.py stats
```

Stdlib only.
