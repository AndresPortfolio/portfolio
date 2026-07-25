"""
SQLite lead funnel with multi-step intake + digest.

Shows a tiny CRM-lite state machine: questions → score → hot flag → digest.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).with_name("leads.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    company TEXT NOT NULL,
    budget_band TEXT NOT NULL,
    timeline TEXT NOT NULL,
    score INTEGER NOT NULL,
    hot INTEGER NOT NULL DEFAULT 0,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS intake_sessions (
    session_id TEXT PRIMARY KEY,
    step TEXT NOT NULL,
    payload TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

STEPS = ("name", "company", "budget", "timeline", "done")


@dataclass(frozen=True)
class ScoredLead:
    name: str
    company: str
    budget_band: str
    timeline: str
    score: int
    hot: bool
    notes: str


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def score_lead(budget_band: str, timeline: str) -> tuple[int, bool, str]:
    budget_scores = {
        "under-1k": 15,
        "1k-5k": 45,
        "5k-20k": 75,
        "20k+": 95,
    }
    timeline_bonus = {
        "this-week": 15,
        "this-month": 8,
        "later": 0,
    }
    score = budget_scores.get(budget_band, 5) + timeline_bonus.get(timeline, 0)
    notes = []
    if budget_band in {"5k-20k", "20k+"}:
        notes.append("budget-qualified")
    if timeline == "this-week":
        notes.append("urgent-timeline")
    hot = score >= 70
    return score, hot, ",".join(notes)


def upsert_session(session_id: str, step: str, payload: dict) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO intake_sessions (session_id, step, payload, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
              step=excluded.step,
              payload=excluded.payload,
              updated_at=excluded.updated_at
            """,
            (session_id, step, json.dumps(payload), utc_now()),
        )


def get_session(session_id: str) -> tuple[str, dict] | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT step, payload FROM intake_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
    if not row:
        return None
    return row["step"], json.loads(row["payload"])


def persist_lead(lead: ScoredLead) -> int:
    with connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO leads (name, company, budget_band, timeline, score, hot, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                lead.name,
                lead.company,
                lead.budget_band,
                lead.timeline,
                lead.score,
                int(lead.hot),
                lead.notes,
                utc_now(),
            ),
        )
        return int(cur.lastrowid)


def answer(session_id: str, value: str) -> str:
    state = get_session(session_id)
    if state is None:
        upsert_session(session_id, "name", {})
        state = ("name", {})

    step, payload = state
    value = value.strip()
    if not value:
        prompts = {
            "name": "What is the prospect's name?",
            "company": "Company name?",
            "budget": "Budget band? [under-1k|1k-5k|5k-20k|20k+]",
            "timeline": "Timeline? [this-week|this-month|later]",
            "done": "intake complete — start a new --session",
        }
        return f"step={step} ask: {prompts.get(step, step)}"

    if step == "name":
        payload["name"] = value
        upsert_session(session_id, "company", payload)
        return "step=company ask: Company name?"
    if step == "company":
        payload["company"] = value
        upsert_session(session_id, "budget", payload)
        return "step=budget ask: Budget band? [under-1k|1k-5k|5k-20k|20k+]"
    if step == "budget":
        if value not in {"under-1k", "1k-5k", "5k-20k", "20k+"}:
            return "step=budget ask: choose under-1k | 1k-5k | 5k-20k | 20k+"
        payload["budget"] = value
        upsert_session(session_id, "timeline", payload)
        return "step=timeline ask: Timeline? [this-week|this-month|later]"
    if step == "timeline":
        if value not in {"this-week", "this-month", "later"}:
            return "step=timeline ask: choose this-week | this-month | later"
        payload["timeline"] = value
        score, hot, notes = score_lead(payload["budget"], payload["timeline"])
        lead = ScoredLead(
            name=payload["name"],
            company=payload["company"],
            budget_band=payload["budget"],
            timeline=payload["timeline"],
            score=score,
            hot=hot,
            notes=notes,
        )
        lead_id = persist_lead(lead)
        upsert_session(session_id, "done", payload)
        flag = "HOT" if hot else "cold"
        return f"step=done lead_id={lead_id} score={score} ({flag}) notes={notes or '-'}"

    return "step=done intake complete — start a new --session to capture another lead"



def list_hot() -> None:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, name, company, budget_band, timeline, score, notes
            FROM leads WHERE hot = 1 ORDER BY score DESC, id DESC
            """
        ).fetchall()
    if not rows:
        print("no hot leads")
        return
    for row in rows:
        print(
            f"#{row['id']} {row['score']:3d}  {row['name']} @ {row['company']} "
            f"[{row['budget_band']}/{row['timeline']}] {row['notes']}"
        )


def digest() -> None:
    with connect() as conn:
        total = conn.execute("SELECT COUNT(*) AS c FROM leads").fetchone()["c"]
        hot = conn.execute("SELECT COUNT(*) AS c FROM leads WHERE hot = 1").fetchone()["c"]
        avg = conn.execute("SELECT AVG(score) AS a FROM leads").fetchone()["a"]
    avg_s = f"{avg:.1f}" if avg is not None else "n/a"
    print(f"digest total={total} hot={hot} avg_score={avg_s}")


def main() -> None:
    parser = argparse.ArgumentParser(description="SQLite lead funnel demo")
    sub = parser.add_subparsers(dest="cmd", required=True)

    ans = sub.add_parser("answer", help="advance an intake session")
    ans.add_argument("--session", required=True)
    ans.add_argument("value")

    sub.add_parser("hot", help="list hot leads")
    sub.add_parser("digest", help="print a one-line funnel digest")

    args = parser.parse_args()
    if args.cmd == "answer":
        print(answer(args.session, args.value))
    elif args.cmd == "hot":
        list_hot()
    elif args.cmd == "digest":
        digest()


if __name__ == "__main__":
    main()
