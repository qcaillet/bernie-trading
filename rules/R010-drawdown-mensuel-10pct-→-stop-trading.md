# R010 — Drawdown mensuel -10% → STOP trading

**Sévérité :** `BLOCK`

## Quoi

Si le capital de travail perd 10% sur un mois calendaire, ARRÊT de tout trading jusqu'à fin du mois + debrief obligatoire.

## Comment vérifier

Tracker capital début de mois dans PORTFOLIO.md. À chaque trade clos: check (current - month_start) / month_start. Si < -10% → BLOCK + alerte Telegram + debrief.

## Exemples

Mois commence à 500€, capital tombe à 449€ → BLOCK tous trades. Spawn strategy-evaluator.

## Référence

Cette règle est listée dans `RULES.md`. Sa modification requiert un commit dédié + entrée dans `analysis/`.
