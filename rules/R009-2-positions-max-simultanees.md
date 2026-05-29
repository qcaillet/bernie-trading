# R009 — 2 positions max simultanées

**Sévérité :** `BLOCK`

## Quoi

Maximum 2 positions ouvertes en même temps. Sert à garder la concentration et limiter l'exposition.

## Comment vérifier

Avant ouverture: `len(open_positions) < 2`. Sinon BLOCK.

## Exemples

1 position SPY ouverte + 1 position NVDA ouverte → 3ème trade ? BLOCK

## Référence

Cette règle est listée dans `RULES.md`. Sa modification requiert un commit dédié + entrée dans `analysis/`.
