# Health board

## What this demonstrates

- Concurrent HTTP health probes across a small service fleet
- Retries, latency measurement, degraded vs down status
- One-line digest **or** JSON output for ops agents
- Non-zero exit codes for cron / launchd alerting (`--strict` optional)

## How to run

```bash
cd examples/health-board

python check.py messaging-bot=http://127.0.0.1:8080/health
python check.py --json api=http://127.0.0.1:8090/health worker=http://127.0.0.1:8091/health
python check.py --strict messaging-bot=http://127.0.0.1:8080/health
```

Optional config file (`probes.json`):

```json
[{"name": "api", "url": "http://127.0.0.1:8090/health"}]
```

```bash
python check.py --config probes.json
```

Stdlib only.
