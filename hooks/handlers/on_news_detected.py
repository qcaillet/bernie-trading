#!/usr/bin/env python3
"""
Handler: on_news_detected.

Notif Telegram + émet needs_analysis pour spawn news-analyzer côté Bernie main.

Payload:
{
    "source": "SEC EDGAR",
    "ticker": "NVDA",
    "form": "8-K",
    "items_codes": ["2.02"],
    "items_meaning": ["Results of Operations"],
    "url": "...",
    "filed_at": "ISO",
    "severity": "high|medium|low"
}
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, (ROOT / "scripts").as_posix())
from telegram import Telegram


def handle(payload: dict, event: dict) -> dict:
    tg = Telegram()
    severity = payload.get("severity", "medium")
    emoji = {"high": "🚨", "medium": "📢", "low": "ℹ️"}.get(severity, "📢")
    items_meaning = payload.get("items_meaning", [])
    items_str = "\n".join(f"  • {m}" for m in items_meaning) if items_meaning else "(no items)"
    msg = (
        f"{emoji} *News détectée*\n\n"
        f"`{payload.get('ticker', '?')}` — {payload.get('form', '?')}\n"
        f"{items_str}\n\n"
        f"URL : {payload.get('url', '')}\n"
        f"Severity: {severity}"
    )
    tg.send(msg, silent=(severity == "low"))

    # Demande analyse profonde côté Bernie main
    sys.path.insert(0, (ROOT / "hooks").as_posix())
    from dispatcher import emit_event
    emit_event("needs_news_analysis", payload)
    return {"telegram_sent": True}
