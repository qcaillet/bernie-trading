#!/usr/bin/env python3
"""
Helper centralisé pour l'API eToro (mode démo par défaut).

Usage:
    from etoro import EToro
    api = EToro()
    api.search("SPY") -> instrument
    api.rate(3000) -> {ask, bid, ...}
    api.open(instr_id, amount_eur, is_buy, sl, tp) -> {order_id, position_id, open_rate}
    api.close(position_id, instrument_id) -> {close_rate}
    api.portfolio() -> {credit, positions}
"""

import json
import os
import sys
import time
import uuid
from pathlib import Path

import requests

SECRETS_PATH = Path.home() / ".openclaw/workspace/.secrets/etoro_keys"
BASE = "https://public-api.etoro.com/api/v1"


class EToroError(Exception):
    pass


class EToro:
    def __init__(self, demo: bool = True, secrets_path: Path = SECRETS_PATH):
        self.demo = demo
        self.seg = "demo/" if demo else ""
        self.pub, self.priv = self._load_keys(secrets_path)

    @staticmethod
    def _load_keys(path: Path) -> tuple[str, str]:
        if not path.exists():
            raise EToroError(f"Secrets introuvables: {path}")
        pub = priv = None
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == "ETORO_PUBLIC_KEY":
                pub = v.strip()
            elif k.strip() == "ETORO_PRIVATE_KEY":
                priv = v.strip()
        if not pub or not priv:
            raise EToroError("ETORO_PUBLIC_KEY / ETORO_PRIVATE_KEY manquantes")
        return pub, priv

    def _h(self) -> dict:
        return {
            "x-api-key": self.pub,
            "x-user-key": self.priv,
            "x-request-id": str(uuid.uuid4()),
            "Content-Type": "application/json",
        }

    def _get(self, path: str, params: dict | None = None) -> dict:
        r = requests.get(f"{BASE}{path}", headers=self._h(), params=params, timeout=20)
        if r.status_code >= 400:
            raise EToroError(f"GET {path} -> {r.status_code}: {r.text[:300]}")
        return r.json()

    def _post(self, path: str, body: dict) -> dict:
        r = requests.post(f"{BASE}{path}", headers=self._h(), json=body, timeout=30)
        if r.status_code >= 400:
            raise EToroError(f"POST {path} -> {r.status_code}: {r.text[:300]}")
        return r.json()

    # --- Public API ---

    def search(self, symbol: str) -> dict | None:
        data = self._get("/market-data/search", {"internalSymbolFull": symbol})
        for it in data.get("items", []):
            if it.get("internalSymbolFull") == symbol:
                return it
        return None

    def rate(self, instrument_id: int) -> dict:
        data = self._get("/market-data/instruments/rates", {"instrumentIds": instrument_id})
        rates = data.get("rates", [])
        if not rates:
            raise EToroError(f"Pas de rate pour {instrument_id}")
        return rates[0]

    def portfolio(self) -> dict:
        return self._get(f"/trading/info/{self.seg}portfolio")

    def order_info(self, order_id: int) -> dict:
        return self._get(f"/trading/info/{self.seg}orders/{order_id}")

    def open(self, instrument_id: int, amount_eur: float, is_buy: bool, sl: float, tp: float, leverage: int = 1) -> dict:
        """
        Ouvre une position market. Retourne order_id, position_id, open_rate (après résolution).

        Lève EToroError si rejeté.
        """
        body = {
            "InstrumentId": instrument_id,
            "Amount": amount_eur,
            "Leverage": leverage,
            "IsBuy": is_buy,
            "StopLossRate": sl,
            "TakeProfitRate": tp,
        }
        resp = self._post(f"/trading/execution/{self.seg}market-open-orders/by-amount", body)
        order_id = resp.get("orderForOpen", {}).get("orderID")
        if not order_id:
            raise EToroError(f"Pas d'orderID retourné: {resp}")

        # Résoudre le positionID (attente courte si pending)
        position_id = None
        open_rate = None
        for _ in range(8):  # ~8s max
            info = self.order_info(order_id)
            status = info.get("statusID")
            err = info.get("errorCode")
            if err and err != 0:
                raise EToroError(f"Ordre rejeté (errorCode={err}): {info.get('errorMessage')}")
            positions = info.get("positions", [])
            if positions:
                position_id = positions[0].get("positionID")
                open_rate = positions[0].get("rate")
                break
            time.sleep(1)

        if not position_id:
            raise EToroError(f"Pas de position après ouverture (orderID={order_id}). Vérifier manuellement.")

        return {
            "order_id": order_id,
            "position_id": position_id,
            "open_rate": open_rate,
            "amount_eur": amount_eur,
            "is_buy": is_buy,
            "sl": sl,
            "tp": tp,
            "instrument_id": instrument_id,
        }

    def close(self, position_id: int, instrument_id: int, units_to_deduct: float | None = None) -> dict:
        """
        Ferme une position (totale par défaut, partielle si units_to_deduct fourni).

        ⚠️ Le body DOIT contenir InstrumentId, sinon HTTP 400.
        """
        body = {"InstrumentId": instrument_id}
        if units_to_deduct is not None:
            body["UnitsToDeduct"] = units_to_deduct
        resp = self._post(f"/trading/execution/{self.seg}market-close-orders/positions/{position_id}", body)
        return resp


# --- CLI minimal pour debug ---

def main():
    if len(sys.argv) < 2:
        print("Usage: etoro.py <search|rate|portfolio> [args...]")
        sys.exit(1)
    cmd = sys.argv[1]
    api = EToro()
    if cmd == "search":
        print(json.dumps(api.search(sys.argv[2]), indent=2))
    elif cmd == "rate":
        print(json.dumps(api.rate(int(sys.argv[2])), indent=2))
    elif cmd == "portfolio":
        print(json.dumps(api.portfolio(), indent=2))
    else:
        print(f"commande inconnue: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
