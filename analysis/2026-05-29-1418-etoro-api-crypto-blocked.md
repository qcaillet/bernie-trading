# 2026-05-29 16:18 — eToro API : crypto bloquée 🚨

## Découverte

Test démo end-to-end de l'API eToro :
- ✅ Auth (`x-api-key` + `x-user-key`) fonctionne
- ✅ Lecture market data fonctionne (search, rates)
- ✅ Lecture portfolio démo fonctionne (`GET /trading/info/demo/portfolio`)
- ❌ **Ouverture de position crypto refusée** : `errorCode 759` — "manual Trading is disallowed for this instrument type (10:CRYPTO)"

## Test exécuté

```
POST /api/v1/trading/execution/demo/market-open-orders/by-amount
{
  "InstrumentId": 100000,  // BTC
  "Amount": 10,
  "Leverage": 1,
  "IsBuy": true,
  "StopLossRate": 69193.07,
  "TakeProfitRate": 76476.55
}
→ HTTP 200, mais orderId rejeté plus tard (statusID 4, errorCode 759)
```

L'API accepte l'ordre côté HTTP, mais le moteur de matching le rejette avant exécution. **Aucune position n'a été ouverte.** Le portefeuille démo est resté intact (credit 92 107,59 €).

## Hypothèse cause

Probablement lié à la réglementation **MiCA (EU)** entrée en vigueur fin 2024/2025 : les services crypto retail sont soumis à des contraintes spécifiques. eToro n'a probablement pas inclus la crypto dans le scope de leur API publique (juste les actions / ETF / matières premières).

À confirmer avec eToro Support ou doc plus récente.

## Endpoints qui fonctionnent (testés OK)

| Endpoint | Méthode | Description |
|---|---|---|
| `/market-data/search` | GET | Recherche d'instruments par symbole |
| `/market-data/instruments/rates` | GET | Prix temps réel (bid/ask) |
| `/trading/info/demo/portfolio` | GET | Portefeuille démo complet |
| `/trading/info/demo/orders/{orderId}` | GET | Détails d'un ordre + positions liées |

## Endpoints à tester sur actions/ETF

À faire si on bascule sur actions/ETF :
- `/trading/execution/demo/market-open-orders/by-amount` avec instrumentId d'une action (ex: AAPL, SPY)

## Conséquence stratégie

**Stratégie V1 (crypto BTC/ETH swing) est invalide pour l'auto-exécution via eToro API.**

3 options :
- A. Basculer sur actions US / ETF via eToro API (recommandé)
- B. Rester crypto, mais exécution 100% manuelle par Quentin (perd l'auto)
- C. Changer de broker (Binance / Bitget) pour la crypto

Décision en attente de Quentin.

## Leçon générique

🦞 **Toujours tester la plomberie end-to-end AVANT de cimenter une stratégie.** Si on avait passé 3 semaines à peaufiner la stratégie crypto avant ce test, on aurait perdu un temps fou.

→ **Cette règle entre dans le PLAYBOOK.**
