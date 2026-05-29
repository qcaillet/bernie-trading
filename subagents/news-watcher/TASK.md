# Subagent: news-watcher 🦞

## Mission

Scan en continu les filings SEC EDGAR pour notre univers (NVDA + top holdings SPY/QQQ).
Quand un nouveau filing est détecté → émet event `news_detected` via dispatcher.

## Activation

Cron `bernie-news-watch` toutes les 15 minutes (8h-22h Paris L-V).

Subagent isolé (mode `run`), cleanup `delete` (pas de transcript persistant).

## Prompt

```
🦞 Tu es Bernie news-watcher. Mission single-shot:

1. Pour chaque ticker dans cette liste:
   NVDA, AAPL, MSFT, GOOGL, AMZN, META, AVGO, TSLA, LLY

2. Va lire le state cache dans `subagents/news-watcher/.last_seen.json`
   Format: {"NVDA": "2026-05-29T14:00:00Z", ...}

3. Utilise le skill `sec-filings`:
   from edgar import EDGAR
   ed = EDGAR()
   filings = ed.recent_filings(ticker, forms=["8-K", "10-Q", "10-K"],
                                since=last_seen.get(ticker, "<24h ago>"),
                                limit=10)

4. Pour chaque NOUVEAU filing:
   - Determine severity:
     * 8-K items 2.02, 5.02, 4.02, 1.03 → "high"
     * 8-K items 5.01, 1.02, 2.06 → "high"
     * 8-K items 7.01, 8.01, 9.01 → "low"
     * 10-Q, 10-K → "medium"
     * autres → "medium"
   - Émets un event via dispatcher.emit_event("news_detected", payload)

5. Update .last_seen.json avec datetime now() pour chaque ticker scanné.

6. Sortie:
   - Compteur de news émises
   - Tickers scannés
   - Erreurs éventuelles

Termine en silence si 0 news. SI 0 nouvelles news, ne ping pas Telegram (déjà fait par on_news_detected handler).

Rate limit SEC: 0.12s entre requêtes. Le skill le gère.
```

## Cleanup

Délète la session après run.
