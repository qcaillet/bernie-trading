# Hooks 🦞

## Concept

Les hooks sont des points d'extension déclenchés par des **événements** :
- Un trade vient d'être ouvert → spawn monitor
- Une news SEC importante est détectée → spawn analyzer
- Un trade vient d'être clos → spawn debriefer
- 10 trades clos consécutifs → spawn strategy-evaluator
- Drawdown dépasse seuil → spawn alert + halt

## Architecture

Bernie main session, ou un cron, **écrit un event** dans `events/` :

```json
{
  "kind": "trade_opened" | "trade_closed" | "news_detected" | "batch_completed" | "drawdown_breach",
  "ts": "ISO datetime",
  "payload": {...}
}
```

Le **dispatcher** (`hooks/dispatcher.py`), exécuté périodiquement (ou en réaction directe), lit la queue,
match le kind avec un handler dans `hooks/handlers/on_<kind>.py`, et exécute la logique.

Chaque handler peut :
- Lancer un subagent via `sessions_spawn` (côté Bernie main) — c'est la voie principale
- Appeler un script Python autonome (cas simple)
- Envoyer un message Telegram direct
- Mettre à jour un fichier

## Pourquoi pas plus direct ?

Découplage. Si demain on veut changer la stratégie de monitoring, on touche au handler, pas au code qui détecte l'event.

## Format d'event

```
events/
├── pending/
│   ├── 20260601T143000Z_e001_trade_opened.json
│   └── 20260601T145000Z_e002_news_detected.json
├── processed/
│   └── 20260601T140000Z_e000_trade_opened.json
└── failed/
    └── 20260601T120000Z_xxx_trade_opened.json (with error.log)
```

## Conventions

- Format de nom : `<ISO timestamp Z>_<event_id>_<kind>.json`
- Atomique : on écrit dans `pending/.tmp` puis on rename
- Le dispatcher déplace le fichier vers `processed/` ou `failed/` après traitement

## Handlers actuels

| Hook | Quand déclenché | Action |
|---|---|---|
| `on_trade_opened` | Bernie open un trade | Crée cron monitoring dynamique de la position |
| `on_trade_closed` | Bernie close un trade (SL/TP/manuel) | Spawn `trade-debriefer`, kill monitoring cron, recompute STATS |
| `on_news_detected` | news-watcher push une news | Spawn `news-analyzer` |
| `on_batch_completed` | Multiple de 10 trades clos | Spawn `strategy-evaluator` |
| `on_drawdown_breach` | Drawdown mensuel franchit -10% | Bloque tous les crons trading + alerte Telegram |
| `on_consecutive_losses` | 2 pertes consécutives (R011) | Bloque trades 24h |
