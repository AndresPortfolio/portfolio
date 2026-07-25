# SQLite lead funnel

## What this demonstrates

- Multi-step intake state machine (session → questions → scored lead)
- Budget/timeline scoring with hot-lead flagging
- Operator digest + hot-lead listing
- Lightweight CRM pattern without an external database

## How to run

```bash
cd examples/sqlite-lead-funnel

python funnel.py answer --session demo "Sam"
python funnel.py answer --session demo "Acme"
python funnel.py answer --session demo "5k-20k"
python funnel.py answer --session demo "this-week"
python funnel.py hot
python funnel.py digest
```

Creates local `leads.db` (gitignored). Stdlib only.
