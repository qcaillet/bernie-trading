# R014 — Conformité aux setups documentés

**Sévérité :** `BLOCK`

## Quoi

Aucun trade ne peut être ouvert s'il ne correspond pas EXACTEMENT à un setup documenté dans STRATEGY.md (V2A, V2B, etc.). Pas de freestyle.

## Comment vérifier

Chaque proposal DOIT référencer le setup_id (ex: 'V2A'). Si Bernie est tenté par un trade hors playbook, il doit d'abord proposer une mise à jour de STRATEGY.md à Quentin avant.

## Exemples

Setup 'breakout SPY' identifié, mais pas dans STRATEGY.md → BLOCK + proposer ajout V2C à Quentin.

## Référence

Cette règle est listée dans `RULES.md`. Sa modification requiert un commit dédié + entrée dans `analysis/`.
