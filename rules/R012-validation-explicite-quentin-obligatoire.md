# R012 — Validation explicite Quentin obligatoire

**Sévérité :** `BLOCK`

## Quoi

Aucun ordre n'est exécuté sans réception explicite d'un `trade_ok:<trade_id>` dans inbox/. Pas d'auto-trade unilatéral. Tant qu'on est en phase semi-auto.

## Comment vérifier

Pipeline: send_trade_proposal → polling inbox/ pendant timeout (10 min). Si callback `trade_ok:<trade_id>` reçu → execute. Si `trade_skip:` ou timeout → no trade + log.

## Exemples

Trade proposé, Quentin clique ✅ OUI → execute. Timeout 10min sans réponse → skip + log.

## Référence

Cette règle est listée dans `RULES.md`. Sa modification requiert un commit dédié + entrée dans `analysis/`.
