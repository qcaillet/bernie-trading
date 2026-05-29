# R011 — 2 pertes consécutives → pause obligatoire

**Sévérité :** `BLOCK`

## Quoi

Après 2 trades perdants d'affilée (peu importe la taille de la perte), pause de 24h obligatoire + spawn trade-debriefer.

## Comment vérifier

Tracker streak dans STATS.md. À 2 losses consécutifs → set `pause_until = now + 24h` dans PORTFOLIO.md.

## Exemples

Trade 1 perdu, Trade 2 perdu → no trade pendant 24h, debriefer obligatoire.

## Référence

Cette règle est listée dans `RULES.md`. Sa modification requiert un commit dédié + entrée dans `analysis/`.
