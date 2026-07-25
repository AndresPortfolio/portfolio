# SQLite lead funnel

Multi-step intake state machine → scored lead → hot list / digest.

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
