"""
SQLite lead funnel — structured intake + hot-lead flagging.

Sanitized CRM-lite pattern: capture answers, score them, alert when hot.
No messaging SDK required — CLI-driven so it runs anywhere.
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("leads.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    company TEXT NOT NULL,
    budget_band TEXT NOT NULL,
    score INTEGER NOT NULL,
    hot INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def score_lead(budget_band: str) -> tuple[int, bool]:
    bands = {
        "under-1k": (20, False),
        "1k-5k": (55, False),
        "5k-20k": (80, True),
        "20k+": (95, True),
    }
    return bands.get(budget_band, (10, False))


def add_lead(name: str, company: str, budget_band: str) -> None:
    score, hot = score_lead(budget_band)
    with connect() as conn:
        conn.execute(
            "INSERT INTO leads (name, company, budget_band, score, hot) VALUES (?, ?, ?, ?, ?)",
            (name, company, budget_band, score, int(hot)),
        )
    flag = "🔥 HOT" if hot else "cold"
    print(f"stored {name} @ {company} score={score} ({flag})")


def list_hot() -> None:
    with connect() as conn:
        rows = conn.execute(
            "SELECT name, company, budget_band, score FROM leads WHERE hot = 1 ORDER BY score DESC"
        ).fetchall()
    if not rows:
        print("no hot leads")
        return
    for row in rows:
        print(f"{row['score']:3d}  {row['name']} @ {row['company']} ({row['budget_band']})")


def main() -> None:
    parser = argparse.ArgumentParser(description="SQLite lead funnel demo")
    sub = parser.add_subparsers(dest="cmd", required=True)

    add = sub.add_parser("add", help="capture a lead")
    add.add_argument("--name", required=True)
    add.add_argument("--company", required=True)
    add.add_argument(
        "--budget",
        required=True,
        choices=["under-1k", "1k-5k", "5k-20k", "20k+"],
    )

    sub.add_parser("hot", help="list hot leads")

    args = parser.parse_args()
    if args.cmd == "add":
        add_lead(args.name, args.company, args.budget)
    elif args.cmd == "hot":
        list_hot()


if __name__ == "__main__":
    main()
