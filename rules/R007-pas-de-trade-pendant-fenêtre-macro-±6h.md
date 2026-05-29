# R007 — Pas de trade pendant fenêtre macro ±6h

**Sévérité :** `BLOCK`

## Quoi

Pas de nouvelle position 6h avant ni 6h après un event macro majeur : FOMC, CPI, NFP, GDP US, ECB, BoE.

## Comment vérifier

Skill `earnings-calendar` doit fournir la liste des events. Skill principal doit vérifier qu'aucun event ne tombe dans [now-6h, now+6h].

## Exemples

FOMC annoncé à 20h Paris. Pas de trade entre 14h et 02h le lendemain.

## Référence

Cette règle est listée dans `RULES.md`. Sa modification requiert un commit dédié + entrée dans `analysis/`.
