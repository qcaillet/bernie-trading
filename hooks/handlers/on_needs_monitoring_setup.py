#!/usr/bin/env python3
"""
Handler: on_needs_monitoring_setup.

Quand un trade vient d'être ouvert, on a besoin d'installer un cron de monitoring
dynamique sur cette position. Un script Python ne peut PAS créer de cron OpenClaw
directement (besoin du tool `cron` côté Bernie main session).

Ce handler écrit un flag file `monitoring_pending/{position_id}.json` ET ping
Telegram pour signaler à Bernie main qu'il doit créer le cron à son prochain
réveil (cron 9h/15h/etc.) ou à la prochaine interaction Quentin.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, (ROOT / "scripts").as_posix())
from telegram import Telegram

MONITORING_DIR = ROOT / "monitoring_pending"
MONITORING_DIR.mkdir(exist_ok=True)


def handle(payload: dict, event: dict) -> dict:
    position_id = payload.get("position_id")
    if not position_id:
        return {"error": "no position_id"}

    # Écris flag file
    flag_path = MONITORING_DIR / f"{position_id}.json"
    flag_path.write_text(json.dumps({
        "position_id": position_id,
        "trade_id": payload.get("trade_id"),
        "symbol": payload.get("symbol"),
        "instrument_id": payload.get("instrument_id"),
        "sl": payload.get("sl"),
        "tp": payload.get("tp"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending_cron_creation",
    }, indent=2))

    # Ping Telegram (silent: c'est une note pour Bernie main, pas une alerte)
    tg = Telegram()
    tg.send(
        f"📌 *Monitoring dynamique en attente*\n\n"
        f"Position {position_id} ({payload.get('symbol')}) ouverte.\n"
        f"Bernie main session : créer un cron monitoring 5min (ou 1min si prix < 1.5% du SL/TP) à ton prochain réveil.\n"
        f"Flag file : `monitoring_pending/{position_id}.json`",
        silent=True,
    )
    return {"flag_written": flag_path.as_posix()}
