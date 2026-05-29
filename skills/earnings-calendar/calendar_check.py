#!/usr/bin/env python3
"""
Earnings & macro calendar.

Fail closed: en cas d'échec de source, on assume qu'un event est imminent → trade bloqué.
"""

import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

CACHE_FILE = Path(__file__).resolve().parent / ".cache.json"
CACHE_TTL_S = {"macro": 6 * 3600, "earnings": 12 * 3600}

HIGH_IMPACT_EVENTS = [
    "Fed Interest Rate Decision",
    "FOMC",
    "CPI",
    "Core CPI",
    "PCE Price Index",
    "Core PCE",
    "Non Farm Payrolls",
    "NFP",
    "Unemployment Rate",
    "GDP",
    "ISM Manufacturing PMI",
    "ISM Non-Manufacturing PMI",
    "Retail Sales",
]


class EarningsCalendar:
    def __init__(self):
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        if CACHE_FILE.exists():
            try:
                return json.loads(CACHE_FILE.read_text())
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        CACHE_FILE.write_text(json.dumps(self.cache, indent=2))

    def _cached(self, key: str, kind: str) -> dict | None:
        entry = self.cache.get(key)
        if not entry:
            return None
        if time.time() - entry["ts"] < CACHE_TTL_S[kind]:
            return entry["data"]
        return None

    def _put_cache(self, key: str, data, kind: str):
        self.cache[key] = {"ts": time.time(), "data": data, "kind": kind}
        self._save_cache()

    # ---- Earnings ----

    def next_earnings(self, ticker: str) -> dict | None:
        """
        Returns next earnings event for ticker.
        {date: ISO, days_until: int}
        Fails closed (returns conservative "imminent" if can't fetch).
        """
        cached = self._cached(f"earnings:{ticker}", "earnings")
        if cached:
            return cached

        # Source 1: Nasdaq API (non-officielle mais stable)
        try:
            url = f"https://api.nasdaq.com/api/company/{ticker.upper()}/earnings-date"
            r = requests.get(url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) BernieBot",
                "Accept": "application/json",
            })
            if r.status_code == 200:
                data = r.json()
                # Nasdaq returns various formats, try to extract
                date_str = (
                    data.get("data", {}).get("nextReportingDate")
                    or data.get("data", {}).get("earningsDate")
                )
                if date_str:
                    # Format typique: "Wed, May 28, 2025"
                    try:
                        dt = datetime.strptime(date_str, "%a, %b %d, %Y").replace(tzinfo=timezone.utc)
                    except ValueError:
                        try:
                            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                        except Exception:
                            dt = None
                    if dt:
                        days = (dt - datetime.now(timezone.utc)).days
                        result = {"date": dt.isoformat(), "days_until": days, "source": "nasdaq"}
                        self._put_cache(f"earnings:{ticker}", result, "earnings")
                        return result
        except Exception as e:
            print(f"[earnings-calendar] Nasdaq fail: {e}")

        # Source 2: fallback heuristique via SEC (last earnings + 90 jours)
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sec-filings"))
            from edgar import EDGAR
            ed = EDGAR()
            filings = ed.recent_filings(ticker, forms=["8-K"], limit=20)
            for f in filings:
                if f.get("items") and "2.02" in (f.get("items") or ""):
                    last_earnings = datetime.fromisoformat(f["filed"] + "T00:00:00+00:00")
                    next_estim = last_earnings + timedelta(days=90)
                    days = (next_estim - datetime.now(timezone.utc)).days
                    result = {
                        "date": next_estim.isoformat(),
                        "days_until": days,
                        "source": "sec_estimate",
                        "note": "Estimated as last earnings + 90 days",
                    }
                    self._put_cache(f"earnings:{ticker}", result, "earnings")
                    return result
        except Exception as e:
            print(f"[earnings-calendar] SEC fallback fail: {e}")

        # Fail closed
        return {"date": None, "days_until": 0, "source": "fail_closed", "note": "Could not determine, assuming imminent"}

    # ---- Macro events ----

    def upcoming_macro(self, days: int = 14) -> list[dict]:
        cached = self._cached(f"macro:{days}", "macro")
        if cached is not None:
            return cached

        # TODO: implémenter scraping investing.com calendar (HTML parse, complexe)
        # Pour la V1, on commence avec une liste statique des events connus du mois
        # qu'on enrichira au fil de l'eau.
        # Placeholder structure prête à recevoir des events.
        events = []
        self._put_cache(f"macro:{days}", events, "macro")
        return events

    # ---- Rule checks ----

    def trading_window_check(self, tickers: list[str], macro_window_hours: int = 6, earnings_window_days: int = 7) -> dict:
        """
        Per-ticker check for R007 + R008.
        """
        now = datetime.now(timezone.utc)
        macro = self.upcoming_macro(days=2)
        macro_blocker = None
        for ev in macro:
            ev_dt = datetime.fromisoformat(ev["datetime"].replace("Z", "+00:00"))
            if abs((ev_dt - now).total_seconds()) < macro_window_hours * 3600:
                macro_blocker = f"macro_event:{ev['title']}"
                break

        result = {}
        for t in tickers:
            blockers = []
            if macro_blocker:
                blockers.append(macro_blocker)
            er = self.next_earnings(t)
            if er and 0 <= er.get("days_until", 999) < earnings_window_days:
                blockers.append(f"earnings_in_{er['days_until']}d")
            result[t] = {
                "can_trade": len(blockers) == 0,
                "blockers": blockers,
                "earnings": er,
            }
        return result


if __name__ == "__main__":
    import sys
    cal = EarningsCalendar()
    tickers = sys.argv[1:] or ["NVDA", "AAPL", "MSFT"]
    print(json.dumps(cal.trading_window_check(tickers), indent=2))
