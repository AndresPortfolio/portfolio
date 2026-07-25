# Multi-tenant messaging bot

## What this demonstrates

- Resolve a messaging user → tenant context before doing work
- Feature gates (`require_feature`) and deny-path handling
- Admin allowlist for privileged commands
- Background `/health` HTTP endpoint for process supervisors

Concrete SDK: `python-telegram-bot` (swap the adapter in a real product).

## How to run

```bash
cd examples/messaging-tenant-bot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# put a bot token in .env
set -a; source .env; set +a
python bot.py
```

Health check in another terminal:

```bash
curl -s http://127.0.0.1:8080/health
```

Demo tenants live in `tenants.py` (`owner_user_id` 1001 / 1002). Add your real user id to try `/status` and `/export`.
