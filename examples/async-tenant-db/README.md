# Async tenant store

## What this demonstrates

- SQLAlchemy 2.0 async models and sessions
- Tenant-scoped user resolution
- Plan entitlement checks (`require-plan`)
- Local SQLite DSN with a Postgres-ready swap path (`postgresql+asyncpg://...`)

## How to run

```bash
cd examples/async-tenant-db
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python store.py init
python store.py seed
python store.py resolve user-1001
python store.py require-plan user-1002 --min pro   # deny
python store.py require-plan user-1001 --min pro   # allow
python store.py members acme
```
