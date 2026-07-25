# Async tenant store

SQLAlchemy 2.0 async models + tenant-scoped lookups on SQLite.
Production swap: point the DSN at `postgresql+asyncpg://...`.

```bash
cd examples/async-tenant-db
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python store.py init
python store.py seed
python store.py resolve user-1001
python store.py require-plan user-1002 --min pro   # should deny
python store.py require-plan user-1001 --min pro   # should allow
python store.py members acme
```
