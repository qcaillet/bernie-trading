# R006 — Pas de revenge trading (4h cooldown)

**Sévérité :** `BLOCK`

## Quoi

Après une perte (SL touché), 4h obligatoires sans nouveau trade. Sert à casser la spirale émotionnelle.

## Comment vérifier

Stocker `last_loss_time` dans PORTFOLIO.md state. Si maintenant - last_loss_time < 4h → BLOCK tout nouveau trade.

## Exemples

SL touché à 16h → pas de nouveau trade avant 20h.

## Référence

Cette règle est listée dans `RULES.md`. Sa modification requiert un commit dédié + entrée dans `analysis/`.
