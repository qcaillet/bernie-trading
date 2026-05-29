# Skill: earnings-calendar 🦞

## Quand l'utiliser

- Vérifier les earnings des entreprises de notre univers
- Récupérer le calendrier macro US (FOMC, CPI, NFP, GDP, PMI)
- Appliquer la rule R007 (pas de trade ±6h d'event macro) et R008 (pas de trade si earnings ≤7j)

## Comment l'utiliser

```python
import sys
sys.path.insert(0, "skills/earnings-calendar")
from calendar_check import EarningsCalendar

cal = EarningsCalendar()

# Prochain earnings d'un ticker
next_e = cal.next_earnings("NVDA")  # {date, days_until, ...}

# Events macro à venir (FOMC, CPI, NFP)
events = cal.upcoming_macro(days=14)

# Check rule R007/R008 en un appel
status = cal.trading_window_check(["SPY", "QQQ", "NVDA"])
# status = {"SPY": {"can_trade": True, "blockers": []}, "NVDA": {"can_trade": False, "blockers": ["earnings_in_5d"]}, ...}
```

## Sources

### Earnings
- **Source primaire** : SEC EDGAR (skill `sec-filings`). Détecte les 8-K item 2.02 passés. Pour le FUTUR (date d'earnings à venir), on doit utiliser :
  - Yahoo Finance non-officiel : `https://finance.yahoo.com/calendar/earnings?symbol={ticker}`
  - Nasdaq : `https://api.nasdaq.com/api/calendar/earnings?date={YYYY-MM-DD}`
  - On scrape proprement, avec rate limit raisonnable.

### Macro events
- Investing.com economic calendar : `https://www.investing.com/economic-calendar/`
- Trading Economics : `https://tradingeconomics.com/united-states/calendar`
- On parse les events publics. On garde uniquement les events à **high impact** :
  - Federal Reserve (FOMC meeting, rate decision, minutes)
  - CPI / Core CPI / PCE / Core PCE
  - NFP (Non-Farm Payrolls), Unemployment Rate
  - GDP (advance, prelim, final)
  - PMI Manufacturing/Services, ISM
  - Retail Sales

## Politique de cache

- Données macro : cache 6h (events ne changent pas souvent)
- Earnings calendar : cache 12h (parfois mis à jour)
- Cache file : `skills/earnings-calendar/.cache.json`

## Limitations

- Sources non-officielles peuvent changer de format
- En cas de fail, on FAIL CLOSED : on assume qu'il y a un event (= trade bloqué) plutôt qu'autoriser un trade en aveugle
- À terme, considérer une source payante stable (Finnhub, Polygon, Alpha Vantage)

## Référence

- Code : `skills/earnings-calendar/calendar_check.py`
