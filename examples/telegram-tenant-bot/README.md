# Multi-tenant Telegram bot skeleton

Runnable, sanitized example of patterns used in real multi-tenant Telegram SaaS:

- Resolve a Telegram user → tenant context before doing work
- Keep admin / ops commands on an allowlist
- Expose a tiny `/health` HTTP endpoint for process supervisors

## Run

```bash
cd examples/telegram-tenant-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with a bot token from @BotFather
set -a; source .env; set +a
python bot.py
```

In another terminal:

```bash
curl -s http://127.0.0.1:8080/health
python ../health-board/check.py
```

## Demo tenants

`tenants.py` ships two fake tenants (`acme`, `northwind`) keyed by placeholder Telegram user ids `1001` / `1002`. Point `ADMIN_USER_IDS` at your real id, and add yourself to `_TENANTS` to try `/status`.

## What this is not

Not production source. No billing, no Postgres, no partner portal — just the skeleton that those features hang on.
