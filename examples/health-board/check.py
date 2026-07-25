"""
Tiny fleet health checker pattern.

Given a list of local HTTP health URLs, print a one-line board.
Useful as a cron / launchd helper or as the core of an ops digest.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class Probe:
    name: str
    url: str


DEFAULT_PROBES = (
    Probe("messaging-bot", "http://127.0.0.1:8080/health"),
)


def check(probe: Probe, timeout: float = 2.0) -> tuple[str, str]:
    try:
        with urllib.request.urlopen(probe.url, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            payload = json.loads(raw) if raw.strip().startswith("{") else {}
            ok = bool(payload.get("ok", resp.status == 200))
            return probe.name, "ok" if ok else "degraded"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return probe.name, "down"


def render(results: list[tuple[str, str]]) -> str:
    dots = {"ok": "🟢", "degraded": "🟡", "down": "🔴"}
    return " | ".join(f"{dots.get(status, '?')} {name}" for name, status in results)


def main(argv: list[str]) -> int:
    probes = list(DEFAULT_PROBES)
    # Optional: name=url pairs on the CLI
    for arg in argv[1:]:
        if "=" not in arg:
            continue
        name, url = arg.split("=", 1)
        probes.append(Probe(name=name, url=url))

    results = [check(p) for p in probes]
    print(render(results))
    return 0 if all(status == "ok" for _, status in results) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
