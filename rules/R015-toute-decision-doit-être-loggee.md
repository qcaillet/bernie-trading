# R015 — Toute décision DOIT être loggée

**Sévérité :** `REQUIRE`

## Quoi

Chaque cycle d'analyse (trade pris OU skipped OU rejeté par rule) doit générer une trace dans analysis/ ou trades/.

## Comment vérifier

Si à la fin d'un cron il n'y a aucun fichier créé/modifié → erreur silencieuse, alerter dans STATS.md.

## Exemples

Cron 15h30 tourne, RAS sur les 3 instruments → quand même créer `analysis/YYYY-MM-DD-1530-no-setup.md`.

## Référence

Cette règle est listée dans `RULES.md`. Sa modification requiert un commit dédié + entrée dans `analysis/`.
