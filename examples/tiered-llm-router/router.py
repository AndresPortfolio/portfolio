"""
Tiered LLM router — fast path first, escalate only when needed.

Sanitized pattern from production ops agents. No API keys required:
the default backends are local stubs so you can run and inspect the
routing logic offline. Swap in real OpenAI-compatible clients later.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelReply:
    model: str
    text: str
    confidence: float


class FastStub:
    name = "fast-stub"

    def complete(self, prompt: str) -> ModelReply:
        # Pretend the fast model is unsure on long / ambiguous prompts.
        confidence = 0.9 if len(prompt.split()) < 12 else 0.35
        return ModelReply(
            model=self.name,
            text=f"[fast] ack: {prompt[:80]}",
            confidence=confidence,
        )


class DeepStub:
    name = "deep-stub"

    def complete(self, prompt: str) -> ModelReply:
        return ModelReply(
            model=self.name,
            text=f"[deep] reasoned answer for: {prompt[:80]}",
            confidence=0.95,
        )


@dataclass
class TieredRouter:
    fast: FastStub
    deep: DeepStub
    escalate_below: float = 0.6

    def ask(self, prompt: str) -> ModelReply:
        first = self.fast.complete(prompt)
        if first.confidence >= self.escalate_below:
            return first
        return self.deep.complete(prompt)


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo tiered LLM routing")
    parser.add_argument("prompt", nargs="?", default="restart the billing worker")
    parser.add_argument(
        "--long",
        action="store_true",
        help="use a long prompt that forces escalation",
    )
    args = parser.parse_args()

    prompt = (
        "Diagnose why the billing worker keeps restarting after deploy, "
        "check health, read the last 50 log lines, and propose a fix"
        if args.long
        else args.prompt
    )

    reply = TieredRouter(fast=FastStub(), deep=DeepStub()).ask(prompt)
    print(f"model={reply.model} confidence={reply.confidence:.2f}")
    print(reply.text)


if __name__ == "__main__":
    main()
