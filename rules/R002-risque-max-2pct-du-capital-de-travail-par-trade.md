# R002 — Risque max 2% du capital de travail par trade

**Sévérité :** `BLOCK`

## Quoi

Chaque trade doit risquer au maximum 2% du capital de travail (poche d'entraînement). Au départ : 2% de 500€ = 10€. Si capital évolue, recalculer.

## Comment vérifier

Avant proposal: `risk_eur = abs(entry - sl) * units * conversion` ≤ `working_capital * 0.02`. Sinon réduire la taille de position ou abort.

## Exemples

Capital = 500€, max risque = 10€. Trade SPY entry=750 SL=745 units=2 → risque = 5*2=10€ → OK

## Référence

Cette règle est listée dans `RULES.md`. Sa modification requiert un commit dédié + entrée dans `analysis/`.
