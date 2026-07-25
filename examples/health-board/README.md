# Health board

Concurrent fleet probe with retries, latency, and JSON output.

```bash
cd examples/health-board

# defaults (expect services on :8080 / :8090 — or pass your own)
python check.py messaging-bot=http://127.0.0.1:8080/health

# JSON for an ops agent / dashboard ingest
python check.py --json api=http://127.0.0.1:8090/health worker=http://127.0.0.1:8091/health

# exit 1 on degraded as well as down
python check.py --strict messaging-bot=http://127.0.0.1:8080/health
```

Optional config file (`probes.json`):

```json
[{"name": "api", "url": "http://127.0.0.1:8090/health"}]
```

```bash
python check.py --config probes.json
```
