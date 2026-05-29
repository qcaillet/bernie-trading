#!/usr/bin/env python3
"""
SEC EDGAR client — récupération des filings (sources primaires, légal, gratuit).

⚠️ User-Agent OBLIGATOIRE (sinon 403).
⚠️ Rate limit 10 req/s.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

USER_AGENT = "Bernie Trading bernie@quentin.local"
BASE = "https://data.sec.gov"
ARCHIVE = "https://www.sec.gov/Archives/edgar/data"


# Top tickers de notre univers + leurs CIKs (à étendre)
TICKER_CIK = {
    "NVDA": "0001045810",
    "AAPL": "0000320193",
    "MSFT": "0000789019",
    "GOOGL": "0001652044",
    "AMZN": "0001018724",
    "META": "0001326801",
    "AVGO": "0001730168",
    "TSLA": "0001318605",
    "LLY": "0000059478",
    "COST": "0000909832",
    "NFLX": "0001065280",
    "BRK.B": "0001067983",
}


class EDGAR:
    def __init__(self, user_agent: str = USER_AGENT):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"})

    def _throttle(self):
        time.sleep(0.12)  # ~8 req/s pour rester safe

    def _get(self, url: str) -> dict | str:
        self._throttle()
        r = self.s.get(url, timeout=15)
        if r.status_code >= 400:
            raise RuntimeError(f"GET {url} -> {r.status_code}: {r.text[:200]}")
        if r.headers.get("Content-Type", "").startswith("application/json"):
            return r.json()
        return r.text

    def cik_for(self, ticker: str) -> str | None:
        return TICKER_CIK.get(ticker.upper())

    def recent_filings(self, ticker: str, forms: list[str] | None = None, limit: int = 20, since: str | None = None) -> list[dict]:
        """
        Returns recent filings for a ticker.
        forms: filter (e.g. ["8-K", "10-Q"])
        since: ISO datetime, only filings filed after
        """
        cik = self.cik_for(ticker)
        if not cik:
            raise ValueError(f"CIK inconnu pour {ticker}")
        cik_padded = cik.lstrip("0").zfill(10)
        data = self._get(f"{BASE}/submissions/CIK{cik_padded}.json")
        recent = data.get("filings", {}).get("recent", {})
        if not recent:
            return []
        n = len(recent.get("accessionNumber", []))
        results = []
        since_dt = datetime.fromisoformat(since.replace("Z", "+00:00")) if since else None
        for i in range(n):
            form = recent["form"][i]
            if forms and form not in forms:
                continue
            filed = recent["filingDate"][i]
            filed_dt = datetime.fromisoformat(filed + "T00:00:00+00:00")
            if since_dt and filed_dt < since_dt:
                continue
            accession = recent["accessionNumber"][i]
            primary_doc = recent["primaryDocument"][i]
            accession_clean = accession.replace("-", "")
            doc_url = f"{ARCHIVE}/{int(cik)}/{accession_clean}/{primary_doc}"
            results.append({
                "ticker": ticker.upper(),
                "form": form,
                "filed": filed,
                "accessionNumber": accession,
                "primaryDocument": primary_doc,
                "url": doc_url,
                "primary_doc_url": doc_url,
                "items": recent.get("items", [None]*n)[i],
                "reportDate": recent.get("reportDate", [None]*n)[i],
            })
            if len(results) >= limit:
                break
        return results

    def fetch_filing(self, url: str) -> str:
        """Returns raw HTML/text of a filing document."""
        return self._get(url)

    # ---- Quick summary helpers ----

    @staticmethod
    def summarize_8k_meta(filing: dict) -> dict:
        """
        8-K filings have 'items' codes like 1.01, 2.02, 5.02 etc.
        Each code has a known meaning. We extract these for fast triage.
        """
        ITEM_CODES = {
            "1.01": "Entry into Material Definitive Agreement",
            "1.02": "Termination of Material Definitive Agreement",
            "1.03": "Bankruptcy or Receivership",
            "2.01": "Completion of Acquisition or Disposition",
            "2.02": "Results of Operations and Financial Condition (earnings)",
            "2.03": "Material Direct Financial Obligation",
            "2.04": "Triggering Events",
            "2.05": "Costs Associated with Exit Activities",
            "2.06": "Material Impairments",
            "3.01": "Notice of Delisting / Stock Transfer",
            "3.02": "Unregistered Sales of Equity Securities",
            "4.01": "Changes in Auditor",
            "4.02": "Non-Reliance on Previously Issued Financial Statements",
            "5.01": "Changes in Control",
            "5.02": "Departure/Appointment of Directors or Officers",
            "5.03": "Amendments to Articles / By-Laws",
            "5.07": "Submission of Matters to a Vote of Security Holders",
            "7.01": "Regulation FD Disclosure",
            "8.01": "Other Events",
            "9.01": "Financial Statements and Exhibits",
        }
        items_raw = filing.get("items") or ""
        codes = [c.strip() for c in items_raw.split(",") if c.strip()]
        return {
            "form": filing.get("form"),
            "filed": filing.get("filed"),
            "items_codes": codes,
            "items_meaning": [ITEM_CODES.get(c, "unknown") for c in codes],
            "url": filing.get("url"),
        }


if __name__ == "__main__":
    import sys
    ed = EDGAR()
    ticker = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
    f = ed.recent_filings(ticker, forms=["8-K", "10-Q", "10-K"], limit=5)
    print(f"Recent filings for {ticker}:")
    for filing in f:
        summary = EDGAR.summarize_8k_meta(filing)
        print(json.dumps(summary, indent=2))
