# Browser form runner

Playwright automation against a **local** HTML fixture (no external sites).

```bash
cd examples/browser-form-runner
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

python runner.py
python runner.py --workspace northwind --email ops@northwind.example
```

Uses `fixture.html` via a `file://` URL — good for CI-style smoke tests of form flows.
