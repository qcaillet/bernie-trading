# Skill: trade-journal 🦞

## Quand l'utiliser

À chaque trade :
- Créer un fichier `trades/t_YYYYMMDD_NNN-{SYMBOL}.md` à partir du template
- Logger les events liés au trade (open, monitoring, close)
- Calculer les stats post-trade
- Mettre à jour STATS.md global

## Comment l'utiliser

```python
import sys
sys.path.insert(0, "skills/trade-journal")
from journal import TradeJournal

j = TradeJournal()

# Création d'un trade
trade_id = j.create_trade(
    symbol="SPY",
    side="LONG",
    setup="V2A",
    entry=755.50,
    sl=750.10,
    tp=766.40,
    risk_eur=10,
    rationale="Pullback EMA20 D1 + pin H4 sur support 753",
)
# trade_id = "t_20260601_001"

# Update after execution
j.mark_executed(trade_id, position_id=12345678, open_rate=755.62, order_id=987)

# Append timeline event
j.log_event(trade_id, "Position approche TP1 à 90%")

# Mark closed
j.mark_closed(trade_id, exit_type="TP", exit_rate=766.40, pnl_eur=18.45, duration="2d 4h")

# Recompute global stats
stats = j.compute_stats()
j.write_stats(stats)

# Lookup
trades = j.list_trades(symbol="SPY")
last_loss_time = j.last_loss_time()
recent_streak = j.recent_streak()
```

## Format trade_id

`t_YYYYMMDD_NNN` où NNN est un compteur croissant pour le jour.

Exemple: `t_20260601_001` = premier trade du 1er juin 2026.

## Structure d'un fichier trade

Utilise `trades/TEMPLATE.md` comme base.

Sections :
1. Métadonnées (ID, actif, sens, setup, dates)
2. Plan d'entrée (entry, SL, TP, R/R, taille)
3. Contexte marché
4. Raisonnement d'entrée
5. Validation Quentin (OUI/NON + heure)
6. Exécution (prix réel, slippage, IDs)
7. Évolution (timeline)
8. Sortie (type, prix, P&L, R réalisé)
9. Debrief (qu'a-t-on appris ?)

## STATS.md auto-recalculé

Calculé à partir de l'ensemble des fichiers `trades/t_*.md` :
- Trades totaux / wins / losses / breakeven
- Win rate
- Expectancy en R
- P&L cumulé en €
- Drawdown max
- Streaks
- Découpage par mois, par setup, par actif

## Référence

- Code : `skills/trade-journal/journal.py`
- Template : `trades/TEMPLATE.md`
