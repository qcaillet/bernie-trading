# 2026-05-29 16:22 — eToro API actions/ETF : end-to-end VALIDÉ ✅

## Contexte

Suite au blocage crypto (cf `2026-05-29-1418-etoro-api-crypto-blocked.md`), on bascule sur actions / ETF. Test sur **SPY** (ETF S&P500) pour valider toute la chaîne.

## Résultat

✅ **Pipeline complet fonctionnel.**

| Étape | Endpoint | Résultat |
|---|---|---|
| Search | `GET /market-data/search?internalSymbolFull=SPY` | OK, `id=3000` |
| Rate | `GET /market-data/instruments/rates?instrumentIds=3000` | ask=756.72, bid=756.71 |
| Open | `POST /trading/execution/demo/market-open-orders/by-amount` | HTTP 200, orderID retourné |
| Get order | `GET /trading/info/demo/orders/{orderId}` | positionID extrait |
| Close | `POST /trading/execution/demo/market-close-orders/positions/{positionId}` | HTTP 200 avec `{"InstrumentId": <id>}` |
| Portfolio | `GET /trading/info/demo/portfolio` | 0 position après close |

## Coût mesuré

P&L sur ouverture+fermeture immédiate : **-0.03 € sur 10 €** (0.3 % spread aller-retour). Normal pour SPY, raisonnable.

## Pièges identifiés (à intégrer dans helpers)

### 🚨 Piège n°1 : body du close

La doc montre `{"UnitsToDeduct": null}`. ÇA NE MARCHE PAS. L'API exige **obligatoirement** :

```json
{"InstrumentId": <id de l'instrument>}
```

Optionnellement, `UnitsToDeduct` pour fermeture partielle. Mais `InstrumentId` est requis.

### 🚨 Piège n°2 : orderID vs positionID

L'open renvoie un **orderID** (ex `356017140`). Pour fermer il faut le **positionID** (ex `3527995659`).

Pipeline obligatoire après open :
1. `GET /trading/info/demo/orders/{orderId}` → récupérer `positions[0].positionID`
2. Attendre un peu (1-3s) que l'exécution soit faite (statusID passe à 3)
3. Utiliser ce positionID pour close ou monitor

### ℹ️ Note : `isExchangeOpen: false` sur SPY

Reçu `false` alors qu'on était en session US ouverte. Le flag semble buggué côté eToro. À ignorer, se fier à `isCurrentlyTradable` + `isBuyEnabled`.

### ℹ️ Note : statusID

- `1` = pending
- `3` = executed
- `4` = rejected (cas crypto)

## Code de référence du flow validé

```python
# Open
body = {
    "InstrumentId": instrument_id,
    "Amount": eur_amount,
    "Leverage": 1,
    "IsBuy": True,    # or False for SHORT
    "StopLossRate": sl_price,
    "TakeProfitRate": tp_price,
}
r = POST /api/v1/trading/execution/demo/market-open-orders/by-amount
order_id = r["orderForOpen"]["orderID"]

# Resolve position
sleep(2)
r = GET /api/v1/trading/info/demo/orders/{order_id}
position_id = r["positions"][0]["positionID"]

# Close
body = {"InstrumentId": instrument_id}
r = POST /api/v1/trading/execution/demo/market-close-orders/positions/{position_id}
```

## Conséquence stratégie

**On part sur actions US / ETF.** Strategy V2 à écrire pour ces marchés.
