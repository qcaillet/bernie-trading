#!/usr/bin/env python3
"""
Handler: on_trade_opened.

Quand un trade vient d'être ouvert :
1. Création d'un cron de monitoring dynamique pour cette position
2. Notification Telegram de confirmation

Payload attendu:
{
    "trade_id": "t_20260601_001",
    "position_id": 3527995659,
    "instrument_id": 3000,
    "symbol": "SPY",
    "side": "LONG",
    "entry_rate": 755.62,
    "sl": 750.10,
    "tp": 766.40,
    "risk_eur": 10
}
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, (ROOT / "scripts").as_posix())
from telegram import Telegram


def handle(payload: dict, event: dict) -> dict:
    tg = Telegram()
    msg = (
        f"✅ *Trade ouvert* — `{payload.get('trade_id', '?')}`\n\n"
        f"*{payload.get('symbol', '?')}* {payload.get('side', '?')}\n"
        f"`Entrée:` ${payload.get('entry_rate', 0):.2f}\n"
        f"`SL:    ` ${payload.get('sl', 0):.2f}\n"
        f"`TP:    ` ${payload.get('tp', 0):.2f}\n"
        f"`Risque:` {payload.get('risk_eur', 0):.2f}€\n"
        f"\nposition_id: `{payload.get('position_id', '?')}`\n"
        f"\nMonitoring dynamique : actif jusqu'à clôture."
    )
    r = tg.send(msg)

    # NOTE: le cron de monitoring dynamique sera créé par Bernie main side via cron.add()
    # Le handler ne peut pas créer de cron OpenClaw directement (pas d'accès au tool ici).
    # Donc on émet juste un event "needs_monitoring_setup" que Bernie main lira au prochain cycle.
    sys.path.insert(0, (ROOT / "hooks").as_posix())
    from dispatcher import emit_event
    emit_event("needs_monitoring_setup", payload)

    return {"telegram_msg_id": r.get("result", {}).get("message_id"), "monitoring_event_emitted": True}
