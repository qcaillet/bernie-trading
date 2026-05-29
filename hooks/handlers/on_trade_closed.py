#!/usr/bin/env python3
"""
Handler: on_trade_closed.

Quand un trade est clos:
1. Update STATS.md via skill trade-journal
2. Notification Telegram avec P&L
3. Émet event 'needs_debrief' pour spawn subagent trade-debriefer côté Bernie main

Payload:
{
    "trade_id": "...",
    "exit_type": "TP|SL|MANUAL",
    "exit_rate": float,
    "pnl_eur": float,
    "duration": "..."
}
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, (ROOT / "scripts").as_posix())
sys.path.insert(0, (ROOT / "skills" / "trade-journal").as_posix())
from telegram import Telegram
from journal import TradeJournal


def handle(payload: dict, event: dict) -> dict:
    j = TradeJournal()

    # Update stats
    stats = j.compute_stats()
    j.write_stats(stats)

    # Check rule R011: 2 consecutive losses → pause
    outcome, n = j.recent_streak()
    pause_triggered = (outcome == "loss" and n >= 2)

    # Telegram
    tg = Telegram()
    pnl = payload.get("pnl_eur", 0)
    emoji = "🟢" if pnl > 0 else ("🔴" if pnl < 0 else "⚪")
    msg = (
        f"{emoji} *Trade clos* — `{payload.get('trade_id', '?')}`\n\n"
        f"Type sortie : `{payload.get('exit_type', '?')}`\n"
        f"Prix sortie : ${payload.get('exit_rate', 0):.2f}\n"
        f"P&L : *{pnl:+.2f}€*\n"
        f"Durée : {payload.get('duration', '-')}\n\n"
        f"📊 *Stats globales*\n"
        f"Trades : {stats['total']}\n"
        f"WR : {stats['winrate']*100:.1f}%\n"
        f"Expectancy : {stats['expectancy_r']:.2f} R\n"
        f"P&L cum : {stats['pnl_cum_eur']:+.2f}€"
    )
    if pause_triggered:
        msg += f"\n\n⚠️ *R011 déclenchée* : 2 pertes consécutives → pause 24h obligatoire."

    tg.send(msg)

    # Emit further events
    sys.path.insert(0, (ROOT / "hooks").as_posix())
    from dispatcher import emit_event
    emit_event("needs_debrief", payload)

    if stats["total"] > 0 and stats["total"] % 10 == 0:
        emit_event("batch_completed", {"batch_size": 10, "total_trades": stats["total"]})

    if pause_triggered:
        emit_event("consecutive_losses_triggered", {"count": n, "pause_until": "now+24h"})

    return {"stats": stats, "pause_triggered": pause_triggered}
