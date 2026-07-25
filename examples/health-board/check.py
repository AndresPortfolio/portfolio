"""
Fleet health board — probe, retry, latency, JSON or one-line digest.

Sanitized ops pattern: something a launchd/cron job can run every minute
and either print a board or exit non-zero for alerting.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Probe:
    name: str
    url: str


@dataclass
class ProbeResult:
    name: str
    status: str  # ok | degraded | down
    latency_ms: float | None
    detail: str
    attempts: int


DEFAULT_PROBES = (
    Probe("messaging-bot", "http://127.0.0.1:8080/health"),
    Probe("api", "http://127.0.0.1:8090/health"),
)


def load_probes(path: Path | None, cli_pairs: list[str]) -> list[Probe]:
    probes: list[Probe] = list(DEFAULT_PROBES)
    if path and path.exists():
        raw = json.loads(path.read_text(encoding="utf-8"))
        probes = [Probe(name=item["name"], url=item["url"]) for item in raw]
    for pair in cli_pairs:
        if "=" not in pair:
            continue
        name, url = pair.split("=", 1)
        probes.append(Probe(name=name.strip(), url=url.strip()))
    # de-dupe by name, last wins
    by_name = {p.name: p for p in probes}
    return list(by_name.values())


def _fetch(url: str, timeout: float) -> tuple[int, dict[str, Any]]:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
        payload: dict[str, Any]
        if raw.strip().startswith("{"):
            payload = json.loads(raw)
        else:
            payload = {}
        return int(resp.status), payload


def check_probe(
    probe: Probe,
    *,
    timeout: float = 2.0,
    retries: int = 2,
    backoff_s: float = 0.35,
) -> ProbeResult:
    last_err = "unreachable"
    for attempt in range(1, retries + 2):
        started = time.perf_counter()
        try:
            status_code, payload = _fetch(probe.url, timeout)
            latency = (time.perf_counter() - started) * 1000
            ok_flag = bool(payload.get("ok", status_code == 200))
            if status_code >= 500:
                return ProbeResult(probe.name, "down", latency, f"http {status_code}", attempt)
            if not ok_flag or status_code >= 400:
                return ProbeResult(
                    probe.name, "degraded", latency, f"http {status_code} ok={ok_flag}", attempt
                )
            return ProbeResult(probe.name, "ok", latency, "healthy", attempt)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
            last_err = f"{type(exc).__name__}: {exc}"
            if attempt <= retries:
                time.sleep(backoff_s * attempt)
    return ProbeResult(probe.name, "down", None, last_err, retries + 1)


def run_board(probes: list[Probe], workers: int = 8) -> list[ProbeResult]:
    results: list[ProbeResult] = []
    with ThreadPoolExecutor(max_workers=max(1, min(workers, len(probes) or 1))) as pool:
        futures = {pool.submit(check_probe, p): p.name for p in probes}
        for fut in as_completed(futures):
            results.append(fut.result())
    order = {p.name: i for i, p in enumerate(probes)}
    results.sort(key=lambda r: order.get(r.name, 999))
    return results


def render_line(results: list[ProbeResult]) -> str:
    dots = {"ok": "🟢", "degraded": "🟡", "down": "🔴"}
    parts = []
    for r in results:
        ms = f"{r.latency_ms:.0f}ms" if r.latency_ms is not None else "n/a"
        parts.append(f"{dots.get(r.status, '?')} {r.name}({ms})")
    return " | ".join(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fleet health board")
    parser.add_argument("pairs", nargs="*", help="optional name=url probes")
    parser.add_argument("--config", type=Path, help="JSON list of {name,url}")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of one-liner")
    parser.add_argument("--strict", action="store_true", help="fail on degraded too")
    args = parser.parse_args(argv)

    probes = load_probes(args.config, args.pairs)
    results = run_board(probes)

    if args.json:
        print(json.dumps([asdict(r) for r in results], indent=2))
    else:
        print(render_line(results))

    bad = {"down"} | ({"degraded"} if args.strict else set())
    return 0 if all(r.status not in bad for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
