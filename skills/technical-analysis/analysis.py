#!/usr/bin/env python3
"""
Technical analysis skill.

Calcule indicateurs (EMA, ATR, RSI), détecte patterns (pin bar, engulfing, breakout),
identifie tendance et niveaux, calcule la taille de position.

Dépendances: numpy (stdlib pas suffisant pour propre).
Si numpy pas dispo, fallback en stdlib (un peu plus lent).
"""

import json
import sys
import uuid
from pathlib import Path
from typing import Literal

import requests

# Import du skill etoro-api pour l'auth
HERE = Path(__file__).resolve().parent
sys.path.insert(0, (HERE.parent / "etoro-api").as_posix())
from client import EToro, BASE  # noqa: E402

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class TA:
    def __init__(self):
        self.api = EToro()

    # ---- Data fetch ----

    # Mapping vers les enums eToro
    INTERVAL_MAP = {
        "1m": "OneMinute", "5m": "FiveMinutes", "10m": "TenMinutes",
        "15m": "FifteenMinutes", "30m": "ThirtyMinutes",
        "1h": "OneHour", "4h": "FourHours",
        "1d": "OneDay", "1w": "OneWeek",
    }

    def fetch_candles(self, instrument_id: int, timeframe: str = "1d", limit: int = 200) -> list[dict]:
        """
        Retrieves OHLCV candles, oldest → newest.
        timeframe: 1m | 5m | 15m | 30m | 1h | 4h | 1d | 1w
        limit max 1000.
        """
        interval = self.INTERVAL_MAP.get(timeframe)
        if not interval:
            raise ValueError(f"timeframe inconnu: {timeframe}")
        limit = min(max(int(limit), 1), 1000)
        # direction=desc renvoie newest first — on inverse pour avoir l'ordre chronologique
        endpoint = f"/market-data/instruments/{instrument_id}/history/candles/desc/{interval}/{limit}"
        data = self.api._get(endpoint)
        # Format: {interval: "...", candles: [{instrumentId, candles: [...]}]}
        items = data.get("candles") or []
        if items and isinstance(items, list) and items and isinstance(items[0], dict) and "candles" in items[0]:
            items = items[0]["candles"]
        normalized = []
        for c in items:
            normalized.append({
                "ts": c.get("fromDate") or c.get("timestamp") or c.get("ts"),
                "open": float(c.get("open")),
                "high": float(c.get("high")),
                "low": float(c.get("low")),
                "close": float(c.get("close")),
                "volume": float(c.get("volume") or 0),
            })
        # Reverse to chronological (oldest -> newest)
        normalized.reverse()
        return normalized

    # ---- Indicators ----

    @staticmethod
    def ema(values: list[float], period: int) -> list[float]:
        if not values:
            return []
        k = 2 / (period + 1)
        out = [values[0]]
        for v in values[1:]:
            out.append(v * k + out[-1] * (1 - k))
        return out

    @staticmethod
    def sma(values: list[float], period: int) -> list[float]:
        if len(values) < period:
            return [None] * len(values)
        out = [None] * (period - 1)
        for i in range(period - 1, len(values)):
            out.append(sum(values[i - period + 1:i + 1]) / period)
        return out

    @classmethod
    def atr(cls, candles: list[dict], period: int = 14) -> list[float]:
        trs = []
        for i, c in enumerate(candles):
            if i == 0:
                trs.append(c["high"] - c["low"])
            else:
                prev_close = candles[i-1]["close"]
                tr = max(c["high"] - c["low"], abs(c["high"] - prev_close), abs(c["low"] - prev_close))
                trs.append(tr)
        return cls.ema(trs, period)  # Wilder uses RMA, EMA is close enough

    @classmethod
    def rsi(cls, candles: list[dict], period: int = 14) -> list[float]:
        closes = [c["close"] for c in candles]
        gains, losses = [0], [0]
        for i in range(1, len(closes)):
            diff = closes[i] - closes[i-1]
            gains.append(max(diff, 0))
            losses.append(max(-diff, 0))
        avg_gain = cls.ema(gains, period)
        avg_loss = cls.ema(losses, period)
        rsi = []
        for ag, al in zip(avg_gain, avg_loss):
            if al == 0:
                rsi.append(100.0)
            else:
                rs = ag / al
                rsi.append(100 - (100 / (1 + rs)))
        return rsi

    # ---- Structure ----

    @classmethod
    def trend(cls, candles: list[dict]) -> Literal["bullish", "bearish", "ranging"]:
        if len(candles) < 200:
            return "ranging"  # pas assez de données
        closes = [c["close"] for c in candles]
        ema20 = cls.ema(closes, 20)[-1]
        ema50 = cls.ema(closes, 50)[-1]
        ema200 = cls.ema(closes, 200)[-1]
        last = closes[-1]
        if last > ema200 and ema20 > ema50:
            return "bullish"
        if last < ema200 and ema20 < ema50:
            return "bearish"
        return "ranging"

    @staticmethod
    def key_levels(candles: list[dict], lookback: int = 50) -> dict:
        recent = candles[-lookback:] if len(candles) > lookback else candles
        highs = sorted([c["high"] for c in recent], reverse=True)[:3]
        lows = sorted([c["low"] for c in recent])[:3]
        return {"resistances": highs, "supports": lows}

    # ---- Patterns ----

    @staticmethod
    def detect_patterns(candles: list[dict]) -> list[str]:
        if len(candles) < 2:
            return []
        patterns = []
        last, prev = candles[-1], candles[-2]
        body = abs(last["close"] - last["open"])
        rng = last["high"] - last["low"]
        if rng == 0:
            return patterns

        # Pin bar
        upper_wick = last["high"] - max(last["close"], last["open"])
        lower_wick = min(last["close"], last["open"]) - last["low"]
        if lower_wick > 2 * body and body / rng < 0.33:
            patterns.append("pin_bar_bull")
        if upper_wick > 2 * body and body / rng < 0.33:
            patterns.append("pin_bar_bear")

        # Engulfing
        if (last["close"] > last["open"] and prev["close"] < prev["open"]
                and last["close"] > prev["open"] and last["open"] < prev["close"]):
            patterns.append("engulfing_bull")
        if (last["close"] < last["open"] and prev["close"] > prev["open"]
                and last["close"] < prev["open"] and last["open"] > prev["close"]):
            patterns.append("engulfing_bear")

        return patterns

    # ---- Sizing ----

    @staticmethod
    def position_size(risk_eur: float, entry_price: float, sl_price: float, eur_usd_rate: float = 1.08) -> dict:
        if entry_price <= 0 or sl_price <= 0:
            raise ValueError("entry / sl invalides")
        if entry_price == sl_price:
            raise ValueError("entry == sl, risque indéfini")
        distance_usd = abs(entry_price - sl_price)
        distance_eur = distance_usd / eur_usd_rate
        units = risk_eur / distance_eur
        position_value_eur = units * entry_price / eur_usd_rate
        return {
            "units": round(units, 6),
            "risk_eur": round(risk_eur, 2),
            "distance_usd": round(distance_usd, 4),
            "distance_eur": round(distance_eur, 4),
            "position_value_eur": round(position_value_eur, 2),
        }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["candles", "indicators", "trend", "patterns", "size"])
    p.add_argument("--instrument", type=int, default=3000)
    p.add_argument("--timeframe", default="1d")
    p.add_argument("--limit", type=int, default=200)
    p.add_argument("--risk", type=float, default=10)
    p.add_argument("--entry", type=float, default=0)
    p.add_argument("--sl", type=float, default=0)
    args = p.parse_args()

    ta = TA()
    if args.cmd == "size":
        print(json.dumps(ta.position_size(args.risk, args.entry, args.sl), indent=2))
    else:
        candles = ta.fetch_candles(args.instrument, args.timeframe, args.limit)
        if args.cmd == "candles":
            print(f"Got {len(candles)} candles; last 3:")
            print(json.dumps(candles[-3:], indent=2))
        elif args.cmd == "indicators":
            closes = [c["close"] for c in candles]
            print(json.dumps({
                "ema20": round(TA.ema(closes, 20)[-1], 4),
                "ema50": round(TA.ema(closes, 50)[-1], 4),
                "ema200": round(TA.ema(closes, 200)[-1], 4),
                "atr14": round(TA.atr(candles, 14)[-1], 4),
                "rsi14": round(TA.rsi(candles, 14)[-1], 2),
            }, indent=2))
        elif args.cmd == "trend":
            print(TA.trend(candles))
        elif args.cmd == "patterns":
            print(json.dumps(TA.detect_patterns(candles[-3:]), indent=2))
