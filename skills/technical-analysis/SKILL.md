# Skill: technical-analysis 🦞

## Quand l'utiliser

À chaque fois que Bernie doit lire la structure technique d'un instrument :
- Calculer EMA, SMA, RSI, ATR
- Identifier la tendance (HH/HL, EMA200, EMA50)
- Détecter pullback, breakout, pin bar, engulfing
- Calculer position sizing à partir d'un risque cible

**Pas de eyeballing LLM** — on utilise des vraies données + maths Python (pandas, numpy).

## Comment l'utiliser

```python
import sys
sys.path.insert(0, "skills/technical-analysis")
from analysis import TA

ta = TA()

# Récupère candles via eToro historical (timeframe: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w)
candles = ta.fetch_candles(instrument_id=3000, timeframe="1d", limit=200)

# Indicateurs
ta.ema(candles, period=20)
ta.atr(candles, period=14)
ta.rsi(candles, period=14)

# Structure
trend = ta.trend(candles)  # "bullish" | "bearish" | "ranging"
levels = ta.key_levels(candles)  # [supports, resistances]

# Patterns
patterns = ta.detect_patterns(candles[-5:])  # ["pin_bar_bull", "engulfing_bear", ...]

# Sizing
size = ta.position_size(
    risk_eur=10,
    entry_price=755.50,
    sl_price=750.10,
    eur_usd_rate=1.08,
)
```

## Endpoint historique eToro

```
GET /api/v1/market-data/instruments/{instrumentId}/candles?timeframe={tf}&limit={n}
```

Timeframes supportés : `1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w`

## Indicateurs implémentés

| Indicateur | Période par défaut | Usage |
|---|---|---|
| EMA | 20, 50, 200 | Tendance |
| ATR | 14 | Volatilité, sizing du SL |
| RSI | 14 | Overbought/oversold, divergences |
| Range | 5+ bougies | Détection consolidation pour V2B |

## Patterns détectés

| Pattern | Logique |
|---|---|
| `pin_bar_bull` | Mèche basse > 2× corps, corps dans le tiers haut, contexte de support |
| `pin_bar_bear` | Inverse |
| `engulfing_bull` | Bougie haussière qui engloutit la précédente baissière |
| `engulfing_bear` | Inverse |
| `breakout_up` | Close > max(N précédentes) + buffer + volume > avg*1.5 |
| `breakout_down` | Inverse |

## Trend logic

```
prix > EMA200(D1) AND EMA20 > EMA50 (D1) → bullish
prix < EMA200(D1) AND EMA20 < EMA50 (D1) → bearish
sinon → ranging
```

## Position sizing

```python
distance_usd = abs(entry - sl)
distance_eur = distance_usd / eur_usd_rate
units = risk_eur / distance_eur
```

⚠️ Cap appliqué : si units < 0.01 → trade impossible (taille trop fine sur eToro). Si units > capital_eur/entry → trade impossible (pas assez de capital).

## Référence

- Code : `skills/technical-analysis/analysis.py`
- Tests : `skills/technical-analysis/test.py`
