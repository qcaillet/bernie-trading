#!/usr/bin/env python3
"""
Helper Telegram pour Bernie.

Usage rapide:
    from telegram import Telegram
    tg = Telegram()
    tg.send("Hello")
    tg.send_trade_proposal(trade_id="t_001", title="Setup SPY LONG", details="...", actions=[("✅ OUI","trade_ok:t_001"),("❌ NON","trade_skip:t_001")])
"""

import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path

SECRETS = Path.home() / ".openclaw/workspace/.secrets"
TOKEN_FILE = SECRETS / "telegram_bot_token"
META_FILE = SECRETS / "telegram_bot_token.meta"
API = "https://api.telegram.org"


class TelegramError(Exception):
    pass


class Telegram:
    def __init__(self, token: str | None = None, chat_id: int | None = None):
        self.token = (token or TOKEN_FILE.read_text().strip())
        if not self.token or ":" not in self.token:
            raise TelegramError("Token Telegram invalide")
        self.chat_id = chat_id or self._load_chat_id()

    def _load_chat_id(self) -> int:
        if META_FILE.exists():
            for line in META_FILE.read_text().splitlines():
                if line.startswith("TELEGRAM_QUENTIN_CHAT_ID="):
                    return int(line.split("=", 1)[1].strip())
        raise TelegramError("TELEGRAM_QUENTIN_CHAT_ID introuvable dans .meta")

    def _call(self, method: str, payload: dict | None = None) -> dict:
        url = f"{API}/bot{self.token}/{method}"
        data = json.dumps(payload).encode() if payload else None
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"} if data else {})
        try:
            with urllib.request.urlopen(req, timeout=70) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore")
            raise TelegramError(f"{method} HTTP {e.code}: {body[:200]}")

    # ---- Envois ----

    def send(self, text: str, parse_mode: str = "Markdown", buttons: list[list[tuple[str, str]]] | None = None, silent: bool = False) -> dict:
        """
        Envoie un message simple ou avec inline keyboard.

        buttons: liste de rangées; chaque rangée = liste de tuples (label, callback_data)
        """
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_notification": silent,
        }
        if buttons:
            payload["reply_markup"] = {
                "inline_keyboard": [
                    [{"text": label, "callback_data": data} for label, data in row]
                    for row in buttons
                ]
            }
        return self._call("sendMessage", payload)

    def edit_message(self, message_id: int, text: str, parse_mode: str = "Markdown", buttons: list[list[tuple[str, str]]] | None = None) -> dict:
        payload = {
            "chat_id": self.chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        if buttons is not None:
            payload["reply_markup"] = {
                "inline_keyboard": [
                    [{"text": label, "callback_data": data} for label, data in row]
                    for row in buttons
                ]
            }
        return self._call("editMessageText", payload)

    def answer_callback(self, callback_id: str, text: str = "", show_alert: bool = False) -> dict:
        return self._call("answerCallbackQuery", {
            "callback_query_id": callback_id,
            "text": text,
            "show_alert": show_alert,
        })

    # ---- Polling ----

    def get_updates(self, offset: int = 0, timeout: int = 50) -> list[dict]:
        resp = self._call("getUpdates", {"offset": offset, "timeout": timeout, "allowed_updates": ["message", "callback_query"]})
        return resp.get("result", [])

    # ---- Helpers métier ----

    def send_trade_proposal(self, trade_id: str, symbol: str, side: str, entry: float, sl: float, tp: float, risk_eur: float, rr: float, reason: str, setup: str = "V2A") -> dict:
        text = (
            f"📊 *Setup {setup} — {symbol} {side}*\n"
            f"\n"
            f"`Entrée:` ${entry:,.2f}\n"
            f"`SL:    ` ${sl:,.2f}\n"
            f"`TP:    ` ${tp:,.2f}\n"
            f"`Risque:` {risk_eur:.2f}€\n"
            f"`R/R:   ` 1:{rr:.1f}\n"
            f"\n"
            f"_Raison :_ {reason}"
        )
        buttons = [[
            ("✅ OUI, trader", f"trade_ok:{trade_id}"),
            ("❌ NON, passer", f"trade_skip:{trade_id}"),
        ]]
        return self.send(text, buttons=buttons)


# ---- CLI ----

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: telegram.py <send|poll> [args]")
        sys.exit(1)
    tg = Telegram()
    cmd = sys.argv[1]
    if cmd == "send":
        msg = " ".join(sys.argv[2:]) or "Test"
        r = tg.send(msg)
        print(json.dumps(r, indent=2)[:400])
    elif cmd == "poll":
        ups = tg.get_updates(offset=int(sys.argv[2]) if len(sys.argv) > 2 else 0, timeout=5)
        print(json.dumps(ups, indent=2)[:2000])
    else:
        print(f"Commande inconnue: {cmd}")


if __name__ == "__main__":
    main()
