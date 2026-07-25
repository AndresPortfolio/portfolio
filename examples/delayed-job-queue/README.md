# Delayed job queue

SQLite-backed queue with `run_at` delays, worker leases, retries, and dead-lettering.

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
