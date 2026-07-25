# Multi-tenant messaging bot skeleton

Runnable, sanitized example of patterns used in real multi-tenant messaging SaaS:

- Resolve a messaging user → tenant context before doing work
- Keep admin / ops commands on an allowlist
- Expose a tiny `/health` HTTP endpoint for process supervisors

Uses `python-telegram-bot` as a concrete messaging SDK so the example actually runs.

## Run

```bash
cd examples/messaging-tenant-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with a bot token from your messaging platform's bot tooling
set -a; source .env; set +a
python bot.py
```

In another terminal:

```bash
curl -s http://127.0.0.1:8080/health
python ../health-board/check.py
```

## Demo tenants

`tenants.py` ships two fake tenants (`acme`, `northwind`) keyed by placeholder user ids `1001` / `1002`. Point `ADMIN_USER_IDS` at your real id, and add yourself to `_TENANTS` to try `/status`.

## What this is not

Not production source. No billing, no Postgres, no partner portal — just the skeleton that those features hang on.
