# REMINDERS.md — Suivis & tâches récurrentes 🦞

> Liste des sujets qu'on a *décidé de traiter plus tard*. Pour chaque, on indique :
> - Le quoi
> - Le quand (cron + condition de déclenchement)
> - Le comment savoir si c'est OK

## R1 — Monitoring dynamique des positions

**Quoi :** créer un cron de monitoring 5min (1min si SL/TP proche) chaque fois qu'une position s'ouvre, et le supprimer à la clôture.

**Déclenchement :** automatique via hook `on_needs_monitoring_setup` (handler créé).

Le handler écrit un flag dans `monitoring_pending/<position_id>.json` ET envoie un Telegram silent. Au prochain réveil, Bernie main lit ce dossier et fait deux choses :
1. Crée un cron OpenClaw `bernie-monitor-pos-<position_id>` qui appelle Bernie pour faire un check rapide de la position
2. Déplace le flag dans `monitoring_active/`

À la clôture du trade (hook `on_trade_closed`), Bernie main doit aussi :
1. Supprimer le cron `bernie-monitor-pos-<position_id>`
2. Déplacer le flag dans `monitoring_closed/`

**Statut :** handler de signalement en place ✅. Création/suppression cron côté Bernie main = TODO au 1er trade.

## R2 — Calendrier macro à enrichir

**Quoi :** la fonction `EarningsCalendar.upcoming_macro()` renvoie une liste vide aujourd'hui (placeholder). Il faut implémenter le scraping Investing.com / Trading Economics OU charger une liste manuelle.

**Rappel automatique :** cron `bernie-reminder-macro-cal` chaque dimanche 19h Paris → Bernie main ouvre ce REMINDERS.md, vérifie l'état du calendrier macro, propose une mise à jour si vide ou périmé.

**Statut :** placeholder ⚠️. À implémenter avant le premier vrai FOMC/CPI/NFP.

**Comment savoir si c'est OK :** la fonction renvoie au moins les 3 prochains events high-impact des 14 jours à venir, avec datetime UTC.

## R3 — Top holdings SPY/QQQ à actualiser

**Quoi :** les listes de top holdings dans `skills/sec-filings/edgar.py` (`TICKER_CIK`) et dans `skills/sec-filings/SKILL.md` sont **statiques au 2026-05-29**. Les holdings changent (rebalancing trimestriel, nouvelles entrées, sorties).

**Rappel automatique :** cron `bernie-reminder-holdings` le 1er du mois à 10h Paris → vérifie si les top-10 SPY/QQQ ont changé (via État Trust Series I — sources publiques SSGA/Invesco).

**Statut :** liste figée au 29 mai 2026 ⚠️.

**Comment savoir si c'est OK :** les top-10 sont vérifiés et à jour ; les CIK de tout nouveau holding ajoutés au dict.

## R4 — Migration potentielle vers WebSocket eToro

**Quoi :** aujourd'hui REST + polling. On a décidé que c'était suffisant pour du swing D1/H4. Si on évolue vers du day trading ou si on rate des coups par retard de polling, basculer en WebSocket.

**Rappel automatique :** aucun (déclenché par observation des stats — strategy-evaluator pourra le suggérer après 50+ trades).

**Statut :** déclassé volontairement ✅ pas urgent.

## R5 — Rotation token GitHub

**Quoi :** token PAT GitHub valide 90 jours (expiration vers fin août 2026).

**Rappel automatique :** cron `bernie-reminder-github-token` 7 jours avant expiration (≈ 21 août 2026, 10h Paris).

**Statut :** token actif jusqu'à ~28 août 2026.

## R6 — Audit des rules après 30 trades

**Quoi :** quand on aura 30 trades clos, revoir les RULES pour voir si certaines n'ont jamais été déclenchées (peut-être trop strictes) ou si certaines pertes auraient été évitées avec une rule additionnelle.

**Déclenchement :** automatique via hook `on_batch_completed` au 30ème trade → spawn `strategy-evaluator` avec instruction spéciale "rules audit".

**Statut :** déclencheur en place via stats counter ✅.

## R7 — Backup hors-GitHub (résilience)

**Quoi :** si GitHub est down ou si on perd l'accès, il faut un backup local. Aujourd'hui : workspace local + git push. Pas de backup tiers.

**Rappel automatique :** cron mensuel `bernie-reminder-backup` 1er du mois → vérifie présence d'un backup récent.

**Statut :** à mettre en place ⚠️ (peut attendre une fois qu'on a vraiment des trades à protéger).

## Comment Bernie utilise ce fichier

- Au début de chaque cron principal (9h, 22h), si une `monitoring_pending/<id>.json` est présente, traiter cette tâche en priorité avant d'aller plus loin.
- Les crons reminder-* envoient un Telegram simple "rappel: tâche RX à traiter" + ouvrent ce fichier pour donner le contexte.
- Quand une tâche est faite, déplacer la section dans `REMINDERS-DONE.md` avec date.
