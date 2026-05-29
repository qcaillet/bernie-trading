#!/usr/bin/env python3
"""
Test démo end-to-end de l'API eToro.

Étapes :
  1. Charge les clés depuis ~/.openclaw/workspace/.secrets/etoro_keys
  2. Récupère le prix actuel BTC (instrumentId 100000)
  3. Ouvre une position démo LONG de 10 € sur BTC avec SL/TP serveur
  4. Vérifie la position
  5. La ferme immédiatement
  6. Affiche P&L

⚠️ Utilise l'endpoint DEMO (pas de risque sur compte réel).
"""

import json
import os
import sys
import time
import uuid
from pathlib import Path

import requests

SECRETS = Path.home() / ".openclaw/workspace/.secrets/etoro_keys"
BASE_REAL = "https://public-api.etoro.com/api/v1"
# La doc mentionne /trading/execution/demo/... pour le mode démo
# On va d'abord essayer endpoint demo, fallback réel si 404

BTC_ID = 100000


def load_keys() -> tuple[str, str]:
    if not SECRETS.exists():
        print(f"❌ Fichier secrets introuvable: {SECRETS}", file=sys.stderr)
        sys.exit(1)
    pub = priv = None
    for line in SECRETS.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() == "ETORO_PUBLIC_KEY":
            pub = v.strip()
        elif k.strip() == "ETORO_PRIVATE_KEY":
            priv = v.strip()
    if not pub or not priv:
        print("❌ Clés manquantes dans le fichier secrets", file=sys.stderr)
        sys.exit(1)
    return pub, priv


def headers(pub: str, priv: str) -> dict:
    return {
        "x-api-key": pub,
        "x-user-key": priv,
        "x-request-id": str(uuid.uuid4()),
        "Content-Type": "application/json",
    }


def get_rate(pub: str, priv: str, instrument_id: int) -> dict:
    url = f"{BASE_REAL}/market-data/instruments/rates"
    r = requests.get(url, headers=headers(pub, priv), params={"instrumentIds": instrument_id}, timeout=15)
    r.raise_for_status()
    return r.json()


def try_open(pub: str, priv: str, instrument_id: int, amount: float, sl: float, tp: float, demo: bool) -> requests.Response:
    seg = "demo/" if demo else ""
    url = f"{BASE_REAL}/trading/execution/{seg}market-open-orders/by-amount"
    body = {
        "InstrumentId": instrument_id,
        "Amount": amount,
        "Leverage": 1,
        "IsBuy": True,
        "StopLossRate": sl,
        "TakeProfitRate": tp,
    }
    print(f"\n➡️  POST {url}")
    print(f"   body: {json.dumps(body)}")
    return requests.post(url, headers=headers(pub, priv), json=body, timeout=20)


def try_close(pub: str, priv: str, position_id, demo: bool) -> requests.Response:
    seg = "demo/" if demo else ""
    url = f"{BASE_REAL}/trading/execution/{seg}market-close-orders/positions/{position_id}"
    print(f"\n➡️  POST {url}")
    return requests.post(url, headers=headers(pub, priv), json={"UnitsToDeduct": None}, timeout=20)


def main() -> None:
    pub, priv = load_keys()
    print(f"✅ Clés chargées (public={len(pub)} chars, private={len(priv)} chars)")

    # 1. Prix actuel BTC
    print("\n=== 1. Prix actuel BTC ===")
    rate = get_rate(pub, priv, BTC_ID)
    print(json.dumps(rate, indent=2)[:800])

    # Extraction du prix
    items = rate.get("rates") or rate.get("items") or []
    if not items and isinstance(rate, list):
        items = rate
    if not items:
        print("❌ Pas de prix retourné, inspect le json ci-dessus")
        sys.exit(1)
    item = items[0]
    last = item.get("lastExecution") or item.get("last") or item.get("currentRate") or item.get("Ask") or item.get("ask")
    ask = item.get("ask") or item.get("Ask") or last
    print(f"\n💰 BTC ask: {ask}")

    # 2. Calcul SL et TP (très larges, juste pour valider le passage d'ordre)
    # On met SL -5% et TP +5%, c'est juste un test, on va clôturer immédiatement
    ask_f = float(ask)
    sl = round(ask_f * 0.95, 2)
    tp = round(ask_f * 1.05, 2)
    print(f"   SL: {sl} | TP: {tp}")

    # 3. Tentative open en demo
    print("\n=== 2. Ouverture position DEMO 10€ BTC LONG ===")
    r = try_open(pub, priv, BTC_ID, 10, sl, tp, demo=True)
    print(f"   HTTP: {r.status_code}")
    print(f"   body: {r.text[:1200]}")

    if r.status_code == 404:
        print("\n⚠️  Endpoint demo non trouvé (404). On NE bascule PAS sur l'endpoint réel sans validation user.")
        sys.exit(2)
    if r.status_code >= 400:
        print(f"\n❌ Erreur ouverture: {r.status_code}")
        sys.exit(3)

    resp = r.json()
    position_id = (
        resp.get("PositionId")
        or resp.get("positionId")
        or resp.get("OrderId")
        or resp.get("orderId")
        or resp.get("Id")
        or resp.get("id")
    )
    print(f"\n✅ Position ouverte. ID: {position_id}")
    print(f"   Full response: {json.dumps(resp, indent=2)[:600]}")

    # 4. Pause + fermeture
    print("\n=== 3. Pause 3s puis fermeture ===")
    time.sleep(3)

    rc = try_close(pub, priv, position_id, demo=True)
    print(f"   HTTP: {rc.status_code}")
    print(f"   body: {rc.text[:1200]}")

    if rc.status_code >= 400:
        print(f"\n❌ Erreur fermeture: {rc.status_code} — POSITION POTENTIELLEMENT ENCORE OUVERTE, vérifie eToro.")
        sys.exit(4)
    print("\n✅ Position fermée. Test end-to-end OK.")


if __name__ == "__main__":
    main()
