# RULES.md — les NEVER absolus 🦞

> Ce fichier prime sur TOUT le reste. Skills, subagents, intuition, opportunité du siècle : si une rule dit non, c'est NON.
> Index des règles. Chaque règle a son propre fichier dans `rules/` avec la logique de check + exemples.

## Rules actives

| ID | Titre | Sévérité | Fichier |
|---|---|---|---|
| R001 | Stop-loss serveur obligatoire | BLOCK | rules/R001-stop-loss-serveur-obligatoire.md |
| R002 | Risque max 2% du capital de travail par trade | BLOCK | rules/R002-risque-max-2pct-du-capital-de-travail-par-trade.md |
| R003 | Risque cumulé max 6% (toutes positions ouvertes) | BLOCK | rules/R003-risque-cumule-max-6pct.md |
| R004 | R/R minimum 1:2 | BLOCK | rules/R004-r-r-minimum-12.md |
| R005 | Pas de moyenne à la baisse | BLOCK | rules/R005-pas-de-moyenne-a-la-baisse.md |
| R006 | Pas de revenge trade (4h cooldown après perte) | BLOCK | rules/R006-pas-de-revenge-trading-(4h-cooldown).md |
| R007 | Pas de trade pendant fenêtre macro (FOMC/CPI/NFP ±6h) | BLOCK | rules/R007-pas-de-trade-pendant-fenêtre-macro-±6h.md |
| R008 | Pas de trade avec earnings ≤7 jours sur l'instrument | BLOCK | rules/R008-pas-de-trade-avec-earnings-dans-7-jours.md |
| R009 | 2 positions max simultanées | BLOCK | rules/R009-2-positions-max-simultanees.md |
| R010 | Drawdown mensuel -10% → STOP trading | BLOCK | rules/R010-drawdown-mensuel-10pct-→-stop-trading.md |
| R011 | 2 pertes consécutives → pause obligatoire (rest jour) | BLOCK | rules/R011-2-pertes-consecutives-→-pause-obligatoire.md |
| R012 | Validation explicite Quentin obligatoire avant exécution | BLOCK | rules/R012-validation-explicite-quentin-obligatoire.md |
| R013 | Pas de nouveau trade ouvert vendredi après 20h (gap WE) | BLOCK | rules/R013-pas-de-nouveau-trade-vendredi-apres-20h.md |
| R014 | Aucun trade sans entrée correspondant aux setups documentés dans STRATEGY.md | BLOCK | rules/R014-conformite-aux-setups-documentes.md |
| R015 | Toute décision DOIT être loggée (trade pris ou skippé) | REQUIRE | rules/R015-toute-decision-doit-être-loggee.md |

## Sévérités

- **BLOCK** — empêche l'action. Si une rule BLOCK dit non, le trade ne se fait pas, même si toutes les autres disent oui.
- **REQUIRE** — l'action doit être faite, sinon erreur (ex: log obligatoire).
- **WARN** — avertissement, action autorisée mais notée (réservé pour futures rules plus souples).

## Pipeline d'évaluation des rules

Avant tout trade, Bernie main DOIT exécuter dans cet ordre :

1. **Pre-check (avant analyse)** — R007, R008, R010, R011, R013 (filtres temporels/contextuels qui empêchent même l'analyse)
2. **Setup check (avant proposition)** — R014 (correspond à un setup documenté ?)
3. **Risk check (avant proposition)** — R002, R003, R004, R009 (math du risque)
4. **Execution check (avant ordre API)** — R001 (SL serveur dans le body de l'ordre), R012 (Quentin a dit OUI)
5. **Post (en parallèle)** — R005 et R006 sont des rules sur les actions ultérieures (pas de DCA, pas de revenge)
6. **Logging (toujours)** — R015

## Ajouter/modifier une rule

Une rule ne peut être ajoutée qu'avec un commit dédié + entrée dans `analysis/` qui explique pourquoi.
Une rule ne peut être désactivée temporairement que par décision explicite de Quentin avec écrite trace dans `analysis/`.

## État du jour

Toutes les rules sont **actives** depuis 2026-05-29.
