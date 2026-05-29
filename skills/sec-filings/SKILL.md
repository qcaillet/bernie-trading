# Skill: sec-filings 🦞

## Quand l'utiliser

Pour récupérer en quasi-temps réel les filings SEC EDGAR sur nos instruments + top holdings :
- 8-K (current report) — événement matériel (annonce, contrat, départ exec, etc.)
- 10-Q / 10-K — rapports financiers
- 4 — insider trades
- 13F — positions des fonds (info importante mais retardée)

Source primaire publique gratuite : EDGAR. Avantage = on lit AVANT que le journaliste interprète.

## Comment l'utiliser

```python
import sys
sys.path.insert(0, "skills/sec-filings")
from edgar import EDGAR

ed = EDGAR()

# Filings récents pour un ticker
filings = ed.recent_filings("NVDA", forms=["8-K", "10-Q"], limit=10)
# [{form, filed, primary_doc_url, ...}]

# Filings depuis date donnée
new_filings = ed.recent_filings("NVDA", since="2026-05-29T00:00:00Z")

# Fetch + parse un 8-K
text = ed.fetch_filing(filing_url)
summary = ed.summarize_8k(text)  # extract key sections
```

## API SEC EDGAR

Base URL : `https://data.sec.gov`

| Endpoint | Usage |
|---|---|
| `/submissions/CIK{cik}.json` | Tous les filings d'une entreprise |
| `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type={form}&dateb=&owner=include&count=40` | Browse par form |
| `https://www.sec.gov/Archives/edgar/data/{cik}/{accession-no-clean}/...` | Documents primaires |

**User-Agent header obligatoire** par SEC : `"Bernie Trading bernie@quentin.local"` (sinon 403).

## CIKs des instruments suivis

| Ticker | CIK | Source |
|---|---|---|
| NVDA | 0001045810 | Direct |
| SPY (top holdings) | dépend du panier | À résoudre dynamiquement |
| QQQ (top holdings) | dépend du panier | À résoudre dynamiquement |

Pour SPY/QQQ : focus sur les top-10 holdings (qui représentent ~35% du panier).

Top SPY (au 2026-05-29, à actualiser) : AAPL, MSFT, NVDA, GOOGL, AMZN, META, BRK.B, AVGO, TSLA, LLY
Top QQQ : MSFT, AAPL, NVDA, AMZN, GOOGL, META, AVGO, TSLA, COST, NFLX

## Limites & rate limiting

- SEC : 10 requêtes/seconde max
- User-Agent obligatoire (sinon 403)
- Pas d'authent, gratuit

## Sécurité

- Données 100% publiques, aucun risque légal
- ⚠️ Ne PAS scraper plus vite que 10 req/s
- ⚠️ Ne PAS croire un filing sans vérifier qu'il est de la bonne entreprise (parfois homonymes)

## Référence

- SEC EDGAR : https://www.sec.gov/edgar
- Format 8-K : https://www.sec.gov/fast-answers/answersform8khtm.html
- Code : `skills/sec-filings/edgar.py`
