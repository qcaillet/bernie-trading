#!/usr/bin/env python3
"""
News-watcher — script autonome (pas un LLM subagent, juste du code mécanique).

Scan SEC EDGAR pour nos tickers, émet event news_detected sur tout filing nouveau.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, (ROOT / "skills" / "sec-filings").as_posix())
sys.path.insert(0, (ROOT / "hooks").as_posix())

from edgar import EDGAR
from dispatcher import emit_event

STATE_FILE = HERE / ".last_seen.json"

TICKERS = [
    "NVDA", "AAPL", "MSFT", "GOOGL", "AMZN",
    "META", "AVGO", "TSLA", "LLY", "COST", "NFLX",
]

SEVERITY_MAP = {
    "8-K": {
        "high": {"1.03", "2.02", "2.06", "4.02", "5.01", "5.02"},
        "low": {"7.01", "8.01", "9.01"},
        # tout le reste → medium
    },
    "10-Q": "medium",
    "10-K": "medium",
    "4": "low",
    "13F-HR": "low",
}


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def severity_of(form: str, items_codes: list[str]) -> str:
    rule = SEVERITY_MAP.get(form)
    if isinstance(rule, str):
        return rule
    if isinstance(rule, dict):
        for c in items_codes:
            if c in rule.get("high", set()):
                return "high"
        for c in items_codes:
            if c in rule.get("low", set()):
                return "low"
        return "medium"
    return "low"


def main():
    ed = EDGAR()
    state = load_state()
    emitted = 0
    errors = []

    for ticker in TICKERS:
        try:
            since = state.get(ticker)  # ISO string ou None
            filings = ed.recent_filings(ticker, forms=["8-K", "10-Q", "10-K"], since=since, limit=10)
            for f in filings:
                meta = EDGAR.summarize_8k_meta(f)
                sev = severity_of(f["form"], meta.get("items_codes", []))
                payload = {
                    "source": "SEC EDGAR",
                    "ticker": ticker,
                    "form": f["form"],
                    "items_codes": meta.get("items_codes", []),
                    "items_meaning": meta.get("items_meaning", []),
                    "url": f["url"],
                    "filed_at": f["filed"],
                    "severity": sev,
                }
                emit_event("news_detected", payload, event_id=f"sec_{ticker}_{f['accessionNumber']}")
                emitted += 1
            # Update state à now (pas au last filing pour éviter de manquer un filing entre deux runs)
            state[ticker] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception as e:
            errors.append({"ticker": ticker, "error": str(e)})

    save_state(state)
    summary = {
        "scanned": len(TICKERS),
        "emitted": emitted,
        "errors": errors,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    main()
