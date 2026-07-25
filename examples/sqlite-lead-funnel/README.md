# SQLite lead funnel

CLI sketch of a lightweight qualification store:

- Capture name / company / budget band
- Score + mark hot leads
- Query hot leads for an operator alert path

```bash
cd examples/sqlite-lead-funnel
python funnel.py add --name "Sam" --company "Acme" --budget 5k-20k
python funnel.py add --name "Alex" --company "Northwind" --budget under-1k
python funnel.py hot
```

Creates a local `leads.db` (gitignored). No messaging SDK, no external services.
