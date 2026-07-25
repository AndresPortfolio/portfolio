# Browser form runner

## What this demonstrates

- Playwright automation for flows without a clean public API
- Fill → submit → assert result text
- Local HTML fixture via `file://` (no external sites)

## How to run

```bash
cd examples/browser-form-runner
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

python runner.py
python runner.py --workspace northwind --email ops@northwind.example
```
