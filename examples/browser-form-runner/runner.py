"""
Playwright form runner against a local HTML fixture.

Demonstrates browser automation for flows without a clean public API:
open page → fill fields → submit → assert result text.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

FIXTURE = Path(__file__).with_name("fixture.html").resolve()


def run(workspace: str, email: str, *, headed: bool = False) -> str:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "Install deps first: pip install -r requirements.txt && playwright install chromium"
        ) from exc

    url = FIXTURE.as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        page = browser.new_page()
        page.goto(url)
        page.fill("#workspace", workspace)
        page.fill("#email", email)
        page.click("#submit")
        page.wait_for_selector("#result:not([hidden])")
        text = page.locator("#result").inner_text().strip()
        browser.close()
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description="Local Playwright form runner")
    parser.add_argument("--workspace", default="acme-ops")
    parser.add_argument("--email", default="owner@acme.example")
    parser.add_argument("--headed", action="store_true")
    args = parser.parse_args()

    if not FIXTURE.exists():
        raise SystemExit(f"missing fixture: {FIXTURE}")

    result = run(args.workspace, args.email, headed=args.headed)
    print(result)
    expected = f"created:{args.workspace}:{args.email}"
    if result != expected:
        print(f"ASSERT FAILED expected={expected!r}", file=sys.stderr)
        raise SystemExit(1)
    print("ok")


if __name__ == "__main__":
    main()
