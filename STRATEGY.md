# Stratégie

## Marchés

- **BTC/USD** et **ETH/USD** uniquement (Phase 1)
- Pas d'altcoin
- Pas d'actions, pas de forex, pas d'options

## Pourquoi BTC/ETH ?

- Marché 24/7 (pas coincé par horaires US)
- Volatilité utile pour apprendre rapidement
- Price action pure, pas de fondamentaux à éplucher
- Narratif macro lisible (Fed, ETF flows, halving, on-chain)
- Frais et spreads compétitifs sur eToro

## Horizon

- **Swing trading** : quelques jours à 2 semaines par trade
- Pas de scalp (trop d'attention requise, spread mange tout)
- Pas de buy-and-hold long terme (on apprend rien, pas l'objectif)

## Setup principal (V1)

### Setup A — Pullback sur support D1 en tendance haussière

**Conditions d'entrée :**
1. Tendance D1 haussière (HH/HL ou EMA200 D1 sous le prix)
2. Pullback vers un support D1 identifié (ancien high, EMA50 D1, niveau psy)
3. Confirmation H4 : bougie de rejet (pin bar, engulfing haussier) ou divergence RSI
4. Volume non-aberrant (pas de panic dump en cours)

**Entrée :** au close H4 confirmé
**Stop-loss :** sous le pivot bas du pullback - buffer 0.3%
**Take-profit 1 :** R = 1.5 (sortie 50% position)
**Take-profit 2 :** R = 3 (sortie restante) ou trail si momentum

### Setup B — Breakout de range avec volume

**Conditions d'entrée :**
1. Range identifié sur D1 (au moins 5 bougies dans la zone)
2. Cassure nette d'une borne (>0.5% au-delà)
3. Volume du breakout > 1.5× volume moyen 20 périodes
4. Retest de la borne cassée tient

**Entrée :** sur le retest réussi
**Stop-loss :** sous la borne du range - buffer 0.5%
**Take-profit 1 :** R = 2 (objectif = hauteur du range projetée)
**Take-profit 2 :** R = 4 si momentum fort

## Calcul de la taille de position

```
Risque par trade = 10 € (2% de 500)
Distance entrée → SL = X €
Quantité = 10 / X
```

Exemple : BTC à 67 000 €, SL à 66 500 € → distance 500 €.
Quantité = 10/500 = 0.02 BTC. Valeur position = 0.02 × 67 000 = 1 340 € (avec levier 1× si margin suffisante).

## Filtres "NO TRADE"

On ne trade PAS si :
- Événement macro majeur dans les 6h (FOMC, CPI, NFP)
- Funding rate extrême (>0.1% sur 8h) sans confirmation
- Volatilité ATR > 2× moyenne 14 jours (marché en panique)
- Quentin n'est pas disponible et position serait laissée seule >12h sans monitoring
- Bernie a déjà eu 2 trades perdants consécutifs sur la journée (pause obligatoire)

## Évolution de la stratégie

Cette stratégie est **V1**. Elle évoluera :
- À chaque batch de 10 trades, debrief approfondi
- Si winrate < 35 % sur 20 trades → revoir setup
- Si expectancy négative sur 20 trades → arrêt + nouvelle stratégie

Toute modification de stratégie est **versionnée dans ce fichier** (avec dates).

## Versions

| Version | Date | Changement |
|---|---|---|
| V1 | 2026-05-29 | Création initiale : 2 setups crypto swing |
