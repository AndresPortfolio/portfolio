# Health board snippet

Minimal “fleet board” pattern: probe local health endpoints and print a one-line status strip.

```bash
# with the tenant-bot example running:
python check.py

# or pass extra probes:
python check.py api=http://127.0.0.1:8090/health worker=http://127.0.0.1:8091/health
```

Exit code `0` only when every probe reports ok — handy for cron / launchd.
