# R013 — Pas de nouveau trade vendredi après 20h

**Sévérité :** `BLOCK`

## Quoi

Le gap de week-end (samedi/dimanche, news Iran/Russie/etc.) peut casser un stop. Pas de nouvelle position après 20h Paris le vendredi.

## Comment vérifier

Check `now.weekday() == 4 and now.hour >= 20` → BLOCK. Les positions OUVERTES peuvent rester (mais on a vérifié qu'elles ont un SL serveur).

## Exemples

Vendredi 21h, setup détecté → no trade. Reprendre lundi.

## Référence

Cette règle est listée dans `RULES.md`. Sa modification requiert un commit dédié + entrée dans `analysis/`.
