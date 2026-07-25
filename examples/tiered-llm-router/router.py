"""
Tiered LLM router with escalation rules, retries, and a transcript log.

Offline stubs by default. Set LLM_API_KEY + LLM_BASE_URL to hit a real
OpenAI-compatible endpoint (works with many providers).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Protocol


ESCALATE_HINTS = re.compile(
    r"\b(diagnos|root cause|stack trace|migrate|refactor|architecture)\b",
    re.I,
)


@dataclass(frozen=True)
class ModelReply:
    model: str
    text: str
    confidence: float
    latency_ms: float
    tier: str


class Completer(Protocol):
    name: str
    tier: str

    def complete(self, prompt: str) -> ModelReply: ...


class FastStub:
    name = "fast-stub"
    tier = "fast"

    def complete(self, prompt: str) -> ModelReply:
        started = time.perf_counter()
        words = len(prompt.split())
        confidence = 0.88 if words < 12 and not ESCALATE_HINTS.search(prompt) else 0.32
        return ModelReply(
            model=self.name,
            text=f"[fast] {prompt.strip()[:120]}",
            confidence=confidence,
            latency_ms=(time.perf_counter() - started) * 1000,
            tier=self.tier,
        )


class DeepStub:
    name = "deep-stub"
    tier = "deep"

    def complete(self, prompt: str) -> ModelReply:
        started = time.perf_counter()
        time.sleep(0.05)  # pretend deeper work costs more
        return ModelReply(
            model=self.name,
            text=f"[deep] reasoned plan for: {prompt.strip()[:120]}",
            confidence=0.94,
            latency_ms=(time.perf_counter() - started) * 1000,
            tier=self.tier,
        )


class OpenAICompatibleClient:
    """Minimal chat-completions client (optional; needs env vars)."""

    def __init__(self, name: str, tier: str, model: str, base_url: str, api_key: str) -> None:
        self.name = name
        self.tier = tier
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def complete(self, prompt: str) -> ModelReply:
        started = time.perf_counter()
        body = json.dumps(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "Be concise. You are an ops assistant."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
            }
        ).encode()
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode())
        text = payload["choices"][0]["message"]["content"]
        return ModelReply(
            model=self.model,
            text=text.strip(),
            confidence=0.75 if self.tier == "fast" else 0.92,
            latency_ms=(time.perf_counter() - started) * 1000,
            tier=self.tier,
        )


@dataclass
class RouteEvent:
    prompt: str
    chosen: ModelReply
    fast_attempt: ModelReply | None
    escalated: bool
    reason: str


@dataclass
class TieredRouter:
    fast: Completer
    deep: Completer
    escalate_below: float = 0.6
    max_retries: int = 1
    transcript: list[RouteEvent] = field(default_factory=list)

    def _call_with_retry(self, client: Completer, prompt: str) -> ModelReply:
        last: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                return client.complete(prompt)
            except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as exc:
                last = exc
                time.sleep(0.2 * (attempt + 1))
        raise RuntimeError(f"{client.name} failed after retries: {last}")

    def ask(self, prompt: str) -> ModelReply:
        force = bool(ESCALATE_HINTS.search(prompt)) or len(prompt.split()) >= 18
        if force:
            deep = self._call_with_retry(self.deep, prompt)
            self.transcript.append(
                RouteEvent(prompt, deep, None, True, "keyword_or_length")
            )
            return deep

        fast = self._call_with_retry(self.fast, prompt)
        if fast.confidence >= self.escalate_below:
            self.transcript.append(RouteEvent(prompt, fast, fast, False, "fast_ok"))
            return fast

        deep = self._call_with_retry(self.deep, prompt)
        self.transcript.append(
            RouteEvent(prompt, deep, fast, True, f"low_confidence:{fast.confidence:.2f}")
        )
        return deep

    def dump_transcript(self, path: Path) -> None:
        serializable = []
        for event in self.transcript:
            serializable.append(
                {
                    "prompt": event.prompt,
                    "escalated": event.escalated,
                    "reason": event.reason,
                    "chosen": asdict(event.chosen),
                    "fast_attempt": asdict(event.fast_attempt) if event.fast_attempt else None,
                }
            )
        path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")


def build_router(use_live: bool) -> TieredRouter:
    if not use_live:
        return TieredRouter(fast=FastStub(), deep=DeepStub())

    key = os.environ.get("LLM_API_KEY", "").strip()
    base = os.environ.get("LLM_BASE_URL", "").strip()
    if not key or not base:
        raise SystemExit("Live mode needs LLM_API_KEY and LLM_BASE_URL")

    fast_model = os.environ.get("LLM_FAST_MODEL", "gpt-4o-mini")
    deep_model = os.environ.get("LLM_DEEP_MODEL", "gpt-4o")
    return TieredRouter(
        fast=OpenAICompatibleClient("fast-live", "fast", fast_model, base, key),
        deep=OpenAICompatibleClient("deep-live", "deep", deep_model, base, key),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Tiered LLM router demo")
    parser.add_argument("prompt", nargs="?", default="restart the billing worker")
    parser.add_argument("--long", action="store_true", help="force a long diagnostic prompt")
    parser.add_argument("--live", action="store_true", help="use OpenAI-compatible HTTP API")
    parser.add_argument("--transcript", type=Path, help="write routing transcript JSON")
    args = parser.parse_args()

    prompt = (
        "Diagnose why the billing worker keeps restarting after deploy, "
        "inspect health endpoints, read recent logs, and propose a root cause fix"
        if args.long
        else args.prompt
    )

    router = build_router(use_live=args.live)
    reply = router.ask(prompt)
    print(
        f"tier={reply.tier} model={reply.model} "
        f"confidence={reply.confidence:.2f} latency_ms={reply.latency_ms:.0f}"
    )
    print(reply.text)
    if args.transcript:
        router.dump_transcript(args.transcript)
        print(f"wrote transcript → {args.transcript}")


if __name__ == "__main__":
    main()
