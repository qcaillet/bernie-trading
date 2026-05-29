#!/usr/bin/env python3
"""
Bernie Telegram Listener — long polling daemon.

Écoute les callbacks Telegram (boutons inline) + les messages texte de Quentin,
écrit les réponses dans une queue de fichiers JSON consommable par les autres
processus (cron jobs, scripts d'exécution).

Architecture:
  - Listener (ce script) : long polling Telegram, écrit ~/.openclaw/workspace/bernie-trading/inbox/
  - Workers (cron jobs) : lisent inbox/ pour récupérer les décisions Quentin

Files générés:
  inbox/<timestamp>_<update_id>.json
    {
      "type": "callback" | "message",
      "from_id": int,
      "data": str (callback_data ou texte),
      "message_id": int,
      "callback_id": str (only for callback),
      "timestamp": ISO
    }

Sécurité:
  - Filtre par chat_id (TELEGRAM_QUENTIN_CHAT_ID) : ignore tout autre expéditeur
  - Offset persistant dans ~/.openclaw/workspace/bernie-trading/.listener_state.json
"""

import json
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Permet l'import de telegram.py voisin
sys.path.insert(0, str(Path(__file__).parent))
from telegram import Telegram, TelegramError

ROOT = Path.home() / ".openclaw/workspace/bernie-trading"
INBOX = ROOT / "inbox"
STATE_FILE = ROOT / ".listener_state.json"

INBOX.mkdir(parents=True, exist_ok=True)

_running = True


def _stop(*_):
    global _running
    _running = False
    print("[listener] stop signal reçu, arrêt en cours...", flush=True)


signal.signal(signal.SIGTERM, _stop)
signal.signal(signal.SIGINT, _stop)


def load_state() -> int:
    if STATE_FILE.exists():
        try:
            return int(json.loads(STATE_FILE.read_text()).get("offset", 0))
        except Exception:
            return 0
    return 0


def save_state(offset: int) -> None:
    STATE_FILE.write_text(json.dumps({"offset": offset, "updated": datetime.now(timezone.utc).isoformat()}))


def write_inbox(update_id: int, payload: dict) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    fn = INBOX / f"{ts}_{update_id}.json"
    fn.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"[listener] inbox << {fn.name}: type={payload['type']} data={payload.get('data', '')[:60]}", flush=True)


def main() -> None:
    tg = Telegram()
    print(f"[listener] start | chat_id={tg.chat_id} | inbox={INBOX}", flush=True)

    offset = load_state()
    print(f"[listener] resume from offset={offset}", flush=True)

    while _running:
        try:
            updates = tg.get_updates(offset=offset, timeout=50)
        except TelegramError as e:
            print(f"[listener] error getUpdates: {e}", flush=True)
            time.sleep(5)
            continue

        for u in updates:
            offset = max(offset, u["update_id"] + 1)

            # callback_query (clic bouton)
            if "callback_query" in u:
                cb = u["callback_query"]
                from_id = cb["from"]["id"]
                if from_id != tg.chat_id:
                    print(f"[listener] ⚠️ callback ignoré (from_id={from_id} != {tg.chat_id})", flush=True)
                    # On répond quand même pour ne pas laisser le spinner
                    try:
                        tg.answer_callback(cb["id"], text="Non autorisé.")
                    except Exception:
                        pass
                    continue

                # Acknowledge tout de suite
                try:
                    tg.answer_callback(cb["id"], text="✅ Reçu")
                except TelegramError as e:
                    print(f"[listener] answer_callback err: {e}", flush=True)

                write_inbox(u["update_id"], {
                    "type": "callback",
                    "from_id": from_id,
                    "data": cb.get("data", ""),
                    "message_id": cb["message"]["message_id"],
                    "callback_id": cb["id"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

            # message texte
            elif "message" in u:
                msg = u["message"]
                from_id = msg["from"]["id"]
                if from_id != tg.chat_id:
                    print(f"[listener] ⚠️ message ignoré (from_id={from_id} != {tg.chat_id})", flush=True)
                    continue
                write_inbox(u["update_id"], {
                    "type": "message",
                    "from_id": from_id,
                    "data": msg.get("text", ""),
                    "message_id": msg["message_id"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

        save_state(offset)

    print(f"[listener] arrêt propre, offset={offset}", flush=True)


if __name__ == "__main__":
    main()
