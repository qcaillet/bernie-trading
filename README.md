# Bernie Trading 🦞

> Trading bot semi-automatique opéré par **Bernie** (lobster, expert finance) avec **Quentin** (humain dans la boucle).

## Mission

Apprendre à trader de manière disciplinée, valider une stratégie en démo eToro, puis passer en réel.
Capital de travail démo : **500 €** (sur compte démo total eToro de 90k €).

## Mode opératoire

1. Bernie analyse le marché à intervalles définis (cron).
2. Bernie identifie un setup et envoie un message WhatsApp à Quentin avec entrée/SL/TP.
3. Quentin valide (OUI / NON) via WhatsApp.
4. Si OUI, Bernie exécute via l'API eToro (SL + TP côté serveur, filet de sécurité garanti).
5. Bernie monitore la position et notifie Quentin si besoin.
6. À la clôture, Bernie loggue tout (résultat, leçons) en `.md` et push GitHub.

## Architecture

```
Bernie (LLM + cron)         Quentin (human)         eToro API
   │                           │                       │
   ├── analyse marché          │                       │
   ├── détecte setup           │                       │
   ├── notif WhatsApp ─────────►                       │
   │                           │                       │
   │                  ◄──── OUI/NON                    │
   │                                                   │
   ├── place ordre + SL + TP ──────────────────────────►
   │                                                   │
   ├── monitore position                               │
   │                                                   │
   ├── log trade en .md                                │
   └── push GitHub                                     │
```

## Structure du repo

- `STRATEGY.md` — stratégie en cours, règles d'entrée/sortie
- `PORTFOLIO.md` — état du portefeuille, capital, règles de risque
- `PLAYBOOK.md` — patterns appris, ce qui marche / ce qui ne marche pas
- `STATS.md` — winrate, expectancy, R moyen, drawdown
- `trades/` — un fichier par trade, ultra détaillé
- `analysis/` — snapshots d'analyses macro/marché
- `scripts/` — utilitaires (calcul stats, helpers API, etc.)

## Phases du projet

- **Phase 1** — Setup + premiers trades manuels validés via WhatsApp (semaines 1-3)
- **Phase 2** — Semi-auto via API eToro sur setups codifiés (semaines 4-8)
- **Phase 3** — Évaluation passage en réel (après 30+ trades, edge prouvé)

## Stack technique

- **LLM principal** : Claude Opus 4.8 via Anthropic Max (`anthropic/claude-opus-4-8`, alias `opus`)
- **Fallbacks LLM** : `openai-codex/gpt-5.5` puis `github-copilot/claude-sonnet-4.6`
- **LLM optionnel manuel** : `openai/gpt-5.5`
- **Marché de départ** : crypto BTC / ETH uniquement
- **Broker** : eToro (compte démo dans un premier temps)
- **API** : eToro Public API (lancée oct 2025) — `https://api-portal.etoro.com`
- **Notif** : WhatsApp via OpenClaw
- **Mémoire** : Markdown + Git (ce repo)
- **Orchestration** : cron OpenClaw

## Règles d'or

- 🚫 Pas de moyenne à la baisse
- 🚫 Pas de revenge trade
- 🚫 Pas de trade sans SL serveur en place
- 🚫 Pas plus de 2 % du capital risqué par trade
- ✅ R/R minimum 1:2
- ✅ Journal écrit pour CHAQUE trade
- ✅ Discipline > intuition

---

**Statut actuel : Phase 1 démarre.**
