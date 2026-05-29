# Skill: etoro-api 🦞

## Quand l'utiliser

À chaque fois que Bernie a besoin de :
- Lire les prix des instruments (rate, ask/bid)
- Récupérer le portfolio (positions ouvertes, credit)
- Ouvrir une position (avec SL/TP serveur)
- Fermer une position (totale ou partielle)
- Obtenir les détails d'un ordre / résoudre un orderID en positionID

## Comment l'utiliser

```python
import sys
sys.path.insert(0, "skills/etoro-api")
from client import EToro

api = EToro()  # mode demo par défaut

# Lecture
spy_rate = api.rate(3000)            # {ask, bid, lastExecution, ...}
spy_info = api.search("SPY")          # full instrument metadata
portfolio = api.portfolio()           # clientPortfolio dict

# Ouverture (SL et TP OBLIGATOIRES — cf R001)
result = api.open(
    instrument_id=3000,
    amount_eur=10,
    is_buy=True,
    sl=720.10,
    tp=790.50,
)
# result = {order_id, position_id, open_rate, ...}

# Fermeture (InstrumentId requis dans le body)
api.close(position_id=result["position_id"], instrument_id=3000)
```

## Endpoints sous le capot

| Méthode | Endpoint | Usage |
|---|---|---|
| GET | `/market-data/search?internalSymbolFull=X` | Résoudre ticker → instrumentId |
| GET | `/market-data/instruments/rates?instrumentIds=X` | Prix temps réel |
| GET | `/trading/info/demo/portfolio` | État portefeuille démo |
| GET | `/trading/info/demo/orders/{orderId}` | Détails ordre + positions liées |
| POST | `/trading/execution/demo/market-open-orders/by-amount` | Ouverture par montant € |
| POST | `/trading/execution/demo/market-close-orders/positions/{positionId}` | Fermeture |

## Pièges connus

⚠️ **Crypto bloquée** — l'API rejette les ordres crypto (`errorCode 759 - manual Trading is disallowed for CRYPTO`). On ne trade QUE actions/ETF.

⚠️ **Close exige InstrumentId** — la doc dit `{"UnitsToDeduct": null}`, c'est FAUX. Il faut `{"InstrumentId": <id>}`. Optionnel : `UnitsToDeduct` pour fermeture partielle.

⚠️ **orderID ≠ positionID** — l'open renvoie un orderID. Pour close il faut le positionID, à récupérer via `GET /trading/info/demo/orders/{orderId}` (le client le fait automatiquement dans `.open()`).

⚠️ **isExchangeOpen est buggué** — toujours `false`. Se fier à `isCurrentlyTradable` + `isBuyEnabled`.

⚠️ **Spread aller-retour** — environ 0.3% AR sur SPY/QQQ/NVDA. À déduire du R/R cible (cf R004).

## Sécurité

- Les clés sont chargées depuis `.secrets/etoro_keys` (chmod 600)
- Auto-détection api-key (~63 chars) vs user-key (~260 chars) par longueur — robuste aux inversions de nommage
- Mode démo par défaut (`demo=True`). Passer en réel demande explicitement `EToro(demo=False)`

## Tests

- Test end-to-end validé le 2026-05-29 sur SPY 10€ démo (open + SL/TP serveur + close)
- Spread mesuré : 0.03€ AR sur 10€ → 0.3%

## Référence

- Doc officielle : https://api-portal.etoro.com
- Analyses : `analysis/2026-05-29-1418-etoro-api-crypto-blocked.md`, `analysis/2026-05-29-1422-etoro-api-actions-OK.md`
- Helper legacy maintenu : `scripts/etoro.py` (alias, pointe vers `skills/etoro-api/client.py`)
