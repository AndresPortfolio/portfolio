"""
Generic multi-tenant messaging bot skeleton.

Sanitized teaching example — not production source.
Shows: tenant resolution, handler layering, allowlisted admin actions,
and a tiny health endpoint a supervisor can poke.

Concrete SDK: python-telegram-bot (swap the adapter in a real product).
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from tenants import TenantError, require_feature, require_tenant, resolve_tenant

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("tenant-bot")


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admin_user_ids: frozenset[int]
    health_port: int

    @classmethod
    def from_env(cls) -> "Settings":
        token = os.environ.get("BOT_TOKEN", "").strip()
        if not token:
            raise SystemExit("Set BOT_TOKEN in the environment (see .env.example)")

        raw_admins = os.environ.get("ADMIN_USER_IDS", "")
        admins = frozenset(
            int(piece.strip()) for piece in raw_admins.split(",") if piece.strip()
        )
        port = int(os.environ.get("HEALTH_PORT", "8080"))
        return cls(bot_token=token, admin_user_ids=admins, health_port=port)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tenant = resolve_tenant(update.effective_user.id if update.effective_user else None)
    name = tenant.display_name if tenant else "there"
    await update.message.reply_text(
        f"Hi {name}. This is a multi-tenant skeleton.\n"
        "Try /status — tenants only see their own slice."
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    try:
        tenant = require_tenant(user.id if user else None)
        require_feature(tenant, "status")
    except TenantError as exc:
        await update.message.reply_text(f"Denied: {exc}")
        return

    await update.message.reply_text(
        "\n".join(
            [
                f"tenant_id: {tenant.tenant_id}",
                f"plan: {tenant.plan}",
                f"seats: {tenant.seat_limit}",
                f"features: {', '.join(sorted(tenant.features)) or '(none)'}",
            ]
        )
    )


async def export_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Pro-plan feature gate example."""
    user = update.effective_user
    try:
        tenant = require_tenant(user.id if user else None)
        require_feature(tenant, "exports")
    except TenantError as exc:
        await update.message.reply_text(f"Denied: {exc}")
        return
    await update.message.reply_text(f"[{tenant.tenant_id}] export queued (demo)")


async def admin_ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Allowlisted admin-only command — pattern for safe ops actions."""
    settings: Settings = context.application.bot_data["settings"]
    user = update.effective_user
    if not user or user.id not in settings.admin_user_ids:
        await update.message.reply_text("Not authorized.")
        return
    await update.message.reply_text("pong — admin path ok")


async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tenant = resolve_tenant(update.effective_user.id if update.effective_user else None)
    if tenant is None:
        await update.message.reply_text("Unmapped user. Ask an admin to add your tenant.")
        return
    await update.message.reply_text(
        f"[{tenant.tenant_id}] Got it. Wire real handlers here."
    )


def start_health_server(port: int) -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path.rstrip("/") != "/health":
                self.send_response(404)
                self.end_headers()
                return
            body = b'{"ok":true,"service":"tenant-bot"}\n'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

    server = HTTPServer(("127.0.0.1", port), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    log.info("health listening on 127.0.0.1:%s/health", port)


def main() -> None:
    settings = Settings.from_env()
    start_health_server(settings.health_port)

    app = Application.builder().token(settings.bot_token).build()
    app.bot_data["settings"] = settings

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("export", export_cmd))
    app.add_handler(CommandHandler("admin_ping", admin_ping))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_text))

    log.info("bot starting (admins=%s)", sorted(settings.admin_user_ids))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
