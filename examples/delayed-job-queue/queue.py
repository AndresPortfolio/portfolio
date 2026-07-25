"""
Delayed job queue with leases, retries, and due-time scheduling.

In-memory + optional SQLite persistence. Models the core of a publish
scheduler without needing Redis/Celery.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

DB_PATH = Path(__file__).with_name("jobs.db")


SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    payload TEXT NOT NULL,
    run_at REAL NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    status TEXT NOT NULL,
    locked_by TEXT,
    locked_until REAL,
    last_error TEXT
);
"""


def utc_ts(dt: datetime | None = None) -> float:
    dt = dt or datetime.now(timezone.utc)
    return dt.timestamp()


@dataclass
class Job:
    id: str
    kind: str
    payload: dict
    run_at: float
    attempts: int
    max_attempts: int
    status: str


class JobQueue:
    def __init__(self, path: Path = DB_PATH) -> None:
        self.path = path
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)

    def enqueue(
        self,
        kind: str,
        payload: dict,
        *,
        delay_s: float = 0.0,
        max_attempts: int = 3,
    ) -> str:
        job_id = uuid.uuid4().hex[:12]
        run_at = utc_ts(datetime.now(timezone.utc) + timedelta(seconds=delay_s))
        self._conn.execute(
            """
            INSERT INTO jobs (id, kind, payload, run_at, attempts, max_attempts, status)
            VALUES (?, ?, ?, ?, 0, ?, 'queued')
            """,
            (job_id, kind, json.dumps(payload), run_at, max_attempts),
        )
        self._conn.commit()
        return job_id

    def claim(self, worker_id: str, lease_s: float = 30.0) -> Job | None:
        now = utc_ts()
        row = self._conn.execute(
            """
            SELECT * FROM jobs
            WHERE status = 'queued'
              AND run_at <= ?
              AND (locked_until IS NULL OR locked_until < ?)
            ORDER BY run_at ASC
            LIMIT 1
            """,
            (now, now),
        ).fetchone()
        if row is None:
            return None

        locked_until = now + lease_s
        cur = self._conn.execute(
            """
            UPDATE jobs
            SET status='running', locked_by=?, locked_until=?, attempts=attempts+1
            WHERE id=? AND status='queued'
            """,
            (worker_id, locked_until, row["id"]),
        )
        self._conn.commit()
        if cur.rowcount != 1:
            return None
        return Job(
            id=row["id"],
            kind=row["kind"],
            payload=json.loads(row["payload"]),
            run_at=row["run_at"],
            attempts=row["attempts"] + 1,
            max_attempts=row["max_attempts"],
            status="running",
        )

    def complete(self, job_id: str) -> None:
        self._conn.execute(
            "UPDATE jobs SET status='done', locked_by=NULL, locked_until=NULL WHERE id=?",
            (job_id,),
        )
        self._conn.commit()

    def fail(self, job_id: str, error: str, *, retry_delay_s: float = 2.0) -> None:
        row = self._conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if row is None:
            return
        if row["attempts"] >= row["max_attempts"]:
            self._conn.execute(
                """
                UPDATE jobs SET status='dead', last_error=?, locked_by=NULL, locked_until=NULL
                WHERE id=?
                """,
                (error, job_id),
            )
        else:
            self._conn.execute(
                """
                UPDATE jobs
                SET status='queued', run_at=?, last_error=?, locked_by=NULL, locked_until=NULL
                WHERE id=?
                """,
                (utc_ts() + retry_delay_s, error, job_id),
            )
        self._conn.commit()

    def stats(self) -> dict[str, int]:
        rows = self._conn.execute(
            "SELECT status, COUNT(*) AS c FROM jobs GROUP BY status"
        ).fetchall()
        return {row["status"]: row["c"] for row in rows}


def handle(job: Job) -> None:
    """Demo handlers — replace with real publish / notify work."""
    if job.kind == "publish":
        account = job.payload.get("account")
        if account == "fail-me":
            raise RuntimeError("simulated publish failure")
        print(f"published account={account} body={job.payload.get('body')!r}")
        return
    if job.kind == "notify":
        print(f"notify → {job.payload.get('to')}: {job.payload.get('message')}")
        return
    raise RuntimeError(f"unknown kind={job.kind}")


def worker_loop(queue: JobQueue, *, seconds: float, worker_id: str) -> None:
    deadline = time.time() + seconds
    while time.time() < deadline:
        job = queue.claim(worker_id)
        if job is None:
            time.sleep(0.2)
            continue
        try:
            handle(job)
            queue.complete(job.id)
            print(f"done job={job.id} attempt={job.attempts}")
        except Exception as exc:  # noqa: BLE001 - demo worker
            queue.fail(job.id, str(exc))
            print(f"fail job={job.id} err={exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Delayed job queue demo")
    sub = parser.add_subparsers(dest="cmd", required=True)

    enq = sub.add_parser("enqueue")
    enq.add_argument("--kind", required=True, choices=["publish", "notify"])
    enq.add_argument("--delay", type=float, default=0.0)
    enq.add_argument("--json", required=True, help='payload JSON, e.g. {"account":"acme"}')

    run = sub.add_parser("work")
    run.add_argument("--seconds", type=float, default=3.0)
    run.add_argument("--worker-id", default="worker-1")

    sub.add_parser("stats")

    demo = sub.add_parser("demo", help="enqueue sample jobs and process them")
    demo.add_argument("--seconds", type=float, default=4.0)

    args = parser.parse_args()
    queue = JobQueue()

    if args.cmd == "enqueue":
        payload = json.loads(args.json)
        job_id = queue.enqueue(args.kind, payload, delay_s=args.delay)
        print(f"enqueued {job_id}")
    elif args.cmd == "work":
        worker_loop(queue, seconds=args.seconds, worker_id=args.worker_id)
    elif args.cmd == "stats":
        print(queue.stats())
    elif args.cmd == "demo":
        queue.enqueue("publish", {"account": "acme", "body": "hello world"}, delay_s=0.5)
        queue.enqueue("notify", {"to": "ops", "message": "publish queued"}, delay_s=0.2)
        queue.enqueue("publish", {"account": "fail-me", "body": "nope"}, delay_s=0.1)
        worker_loop(queue, seconds=args.seconds, worker_id="demo-worker")
        print("stats", queue.stats())


if __name__ == "__main__":
    main()
