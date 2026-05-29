# R003 — Risque cumulé max 6%

**Sévérité :** `BLOCK`

## Quoi

La somme des risques (€) de toutes les positions ouvertes ne peut pas dépasser 6% du capital de travail (30€ au départ).

## Comment vérifier

Avant chaque nouveau trade: `sum(open_position_risks) + new_risk ≤ working_capital * 0.06`. Sinon → BLOCK.

## Exemples

1 position ouverte avec 10€ de risque → un 2ème trade à 10€ OK (total 20€). Un 3ème → BLOCK car 30€=cap.

## Référence

Cette règle est listée dans `RULES.md`. Sa modification requiert un commit dédié + entrée dans `analysis/`.
