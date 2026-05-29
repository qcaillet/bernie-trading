# Architecture Bernie 🦞

> Document de référence — comment Bernie est structuré, qui fait quoi, comment ça communique.

## Vue d'ensemble

```
                          ┌───────────────────────────┐
                          │  Quentin (Telegram + Web) │
                          └─────────────┬─────────────┘
                                        │
                  Inbox <───┐           │ Outbox (Telegram msg)
                            │           ▼
                  ┌─────────┴───────────────────┐
                  │   Bernie main (orchestre)   │
                  │   - chef d'orchestre         │
                  │   - lit RULES.md d'abord     │
                  │   - charge skills à demande  │
                  │   - dispatche aux subagents  │
                  └────────┬────────────────────┘
                           │
        ┌──────────────────┼──────────────────────────────┐
        │                  │                               │
        ▼                  ▼                               ▼
┌──────────────┐  ┌────────────────┐         ┌──────────────────────┐
│   SKILLS     │  │   HOOKS        │         │   SUBAGENTS          │
│ (capacités)  │  │ (event-driven) │         │ (workers isolés)     │
├──────────────┤  ├────────────────┤         ├──────────────────────┤
│ etoro-api    │  │ on_news        │ ───►    │ news-watcher (24/7)  │
│ tech-analysis│  │ on_position_near│        │ news-analyzer        │
│ sec-filings  │  │ on_trade_close  │        │ trade-debriefer      │
│ earnings-cal │  │ on_batch_10     │        │ strategy-evaluator   │
│ trade-journal│  │ on_drawdown     │        │ playbook-curator     │
└──────────────┘  └────────────────┘         └──────────────────────┘
        │                  │                               │
        └──────────────────┴──────────────────┬────────────┘
                                              ▼
                                  ┌──────────────────────┐
                                  │   Mémoire .md / git  │
                                  │   PLAYBOOK, TRADES,  │
                                  │   STATS, ANALYSIS    │
                                  └──────────────────────┘
```

## Principes directeurs

1. **RULES > Skills > Subagents** — les règles dures (RULES.md) priment sur TOUT le reste. Si une rule dit "non", on ne trade pas, point.
2. **Un job par brique** — chaque skill / subagent fait UNE chose. Si on rajoute, on crée une nouvelle brique au lieu de gonfler.
3. **Pas de mémoire magique** — toute info importante DOIT être écrite. Si c'est pas dans un .md, ça n'existe pas pour la session suivante.
4. **Pipeline traçable** — chaque décision a une trace (quel skill consulté, quelle rule appliquée, quel subagent invoqué).
5. **Discipline > intuition** — Bernie peut "sentir" un truc, mais s'il ne passe pas les filtres RULES, no trade.

## Structure du repo

```
bernie-trading/
├── README.md, ARCHITECTURE.md, STRATEGY.md, PORTFOLIO.md, RULES.md
├── PLAYBOOK.md, STATS.md
├── rules/                   # Règles individuelles avec leur logique
│   ├── R001-server-stop-loss.md
│   ├── R002-max-risk-per-trade.md
│   └── ...
├── skills/                  # Capacités spécialisées
│   ├── etoro-api/SKILL.md + code
│   ├── technical-analysis/SKILL.md + code
│   ├── sec-filings/SKILL.md + code
│   ├── earnings-calendar/SKILL.md + code
│   └── trade-journal/SKILL.md + code
├── hooks/                   # Dispatcher d'événements
│   ├── dispatcher.py
│   └── handlers/
│       ├── on_news.py
│       ├── on_position_near_sl.py
│       ├── on_trade_closed.py
│       └── on_batch_completed.py
├── subagents/               # Configs + prompts pour subagents
│   ├── news-watcher/TASK.md
│   ├── news-analyzer/TASK.md
│   ├── trade-debriefer/TASK.md
│   ├── strategy-evaluator/TASK.md
│   └── playbook-curator/TASK.md
├── scripts/                 # Helpers transverses
│   ├── etoro.py             # gardé pour compat, wrappé par skills/etoro-api
│   ├── telegram.py
│   ├── listener.py
│   └── git-push.sh
├── trades/                  # Un .md par trade
├── analysis/                # Snapshots macro, debriefs
├── inbox/                   # Décisions Quentin (listener Telegram)
└── events/                  # Queue d'événements pour le hook dispatcher
```

## Flow d'un trade type

1. **Cron 15h30 (open-us)** — Bernie main démarre
2. Lit `RULES.md` (hard checks)
3. Charge skill `etoro-api`, récupère rates
4. Charge skill `technical-analysis`, calcule structure
5. Charge skill `earnings-calendar`, vérifie pas d'earnings dans 7j
6. Charge skill `sec-filings`, vérifie pas de filing critique récent
7. Si setup détecté → applique chaque rule → si toutes vertes → propose trade
8. Telegram avec boutons OUI/NON via `scripts/telegram.py`
9. Attente inbox (max 10 min)
10. Si OUI → skill `etoro-api`.open() avec SL/TP serveur
11. Hook `on_trade_opened` → écrit événement → declenche monitor dynamique
12. Quand position se ferme (SL ou TP) → Hook `on_trade_closed` → spawn subagent `trade-debriefer`
13. `trade-debriefer` lit le trade, update STATS.md, propose entry playbook si leçon
14. Tous les 10 trades → Hook `on_batch_completed` → spawn `strategy-evaluator`

## Sécurité

- 🔒 Pas de hardcoded secret dans le code. `.secrets/` chmod 700, fichiers chmod 600
- 🔒 Listener filtre `from_id` côté chat Telegram
- 🔒 SL serveur OBLIGATOIRE sur chaque trade — non négociable
- 🔒 Limites systemd sur le listener (mem 200M, CPU 20%)
- 🔒 Kill switch documenté (cf README)

## Versioning

Chaque modification structurelle MAJEURE est documentée dans la section "Versions" de `STRATEGY.md`.
Chaque modif de skill/subagent suit le pattern git classique (commit message clair).
