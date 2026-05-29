# Stratégie V2 — Actions US / ETF

> V1 (crypto BTC/ETH) abandonnée le 2026-05-29 : crypto bloquée à l'auto-exécution via API eToro publique (cf `analysis/2026-05-29-1418-etoro-api-crypto-blocked.md`).
> V2 démarre sur actions US + ETF.

## Univers — 3 instruments seulement

| Symbol | Type | InstrumentID eToro | Pourquoi |
|---|---|---|---|
| **SPY** | ETF S&P500 | 3000 | Très liquide, peu volatil, école de discipline |
| **QQQ** | ETF Nasdaq100 | 3006 | Tech-heavy, narratif clair, volatilité utile |
| **NVDA** | Action Nvidia | 1137 | Star tech, vol élevée, catalyseurs fréquents |

**Pas plus de 3 instruments.** Focus > diversification à ce stade.

## Horizon

- **Swing trading** : 3 à 10 jours par trade en général
- Pas de day trade (frais + stress)
- Pas de buy & hold

## Horaires Bernie (Europe/Paris)

| Heure | Action | Sortie |
|---|---|---|
| **9h00** | Point macro matin (futures US, calendrier eco, news overnight Asie/EU) | Notif WhatsApp synthèse |
| **15h00** | Pré-ouverture US (révise plan, identifie setups potentiels) | Ping si setup à jouer à l'ouverture |
| **15h30** | Ouverture US — surveillance active | Ping immédiat si trade |
| **20h00** | Mi-séance US, check direction journée | Ping si setup tardif |
| **22h00** | **Clôture US** — recap journée, P&L positions, plan lendemain | Notif WhatsApp recap |

Quand position ouverte → checks adaptatifs (5-15 min selon proximité SL/TP, 1 min si imminent).

## Setup principal — V2A : Pullback sur SPY/QQQ dans tendance haussière D1

### Conditions d'entrée

1. **Tendance D1 haussière** : prix > EMA50 D1, EMA20 D1 au-dessus de EMA50 D1
2. **Pullback récent** : retracement vers EMA20 D1 ou support D1 visible (ancien high, niveau psy round)
3. **Confirmation H1 ou H4** : bougie de rejet (pin bar, engulfing haussier) sur le niveau
4. **Volume** : pas de volume aberrant (pas de panic dump)
5. **Pas de news macro majeure dans les 6h** (FOMC, CPI, NFP, earnings de l'instrument lui-même)

### Plan de trade

- **Entrée** : limit ou market au close de la bougie de confirmation
- **Stop-loss serveur** : sous le pivot bas du pullback + buffer 0.3%
- **Take-profit serveur** : R = 2.0 minimum (objectif = ancien high / résistance D1)
- **Taille position** : calculée pour risquer 10 € max (2% de 500 €)
- **R/R minimum requis** : 1:2 (sinon NO TRADE)

## Setup secondaire — V2B : Breakout sur NVDA après consolidation

### Conditions d'entrée

1. **Consolidation D1** : NVDA range ≥ 5 bougies dans une zone étroite
2. **Cassure nette** d'une borne (>0.8% au-delà avec volume)
3. **Volume du breakout** > 1.5× volume moyen 20 périodes
4. **Pas d'earnings dans les 7 jours** suivants
5. **Tendance générale Nasdaq pas baissière** (QQQ > EMA50 D1)

### Plan de trade

- **Entrée** : sur retest réussi de la borne cassée, OU sur close H4 après breakout si retest ne vient pas
- **Stop-loss serveur** : sous la borne du range - buffer 0.5%
- **Take-profit serveur** : R = 2.5 (objectif = hauteur du range projetée)
- **Taille position** : risque 10 € max
- **R/R minimum** : 1:2.5

## Filtres NO TRADE (toujours, peu importe le setup)

- Événement macro majeur dans les 6h (FOMC, CPI, NFP, GDP US)
- Earnings de l'instrument lui-même dans les 7 jours (pour NVDA surtout)
- VIX > 25 (marché en stress) → on attend que ça se calme
- Quentin pas disponible pour valider et position serait laissée >12h sans monitor
- Bernie a déjà eu 2 trades perdants consécutifs sur la journée → pause obligatoire

## Calcul de la taille de position (rappel)

```
Risque par trade = 10 €
Distance entrée → SL = X $ (converti en €)
Quantité (units) = 10 / X
Montant à investir = Quantité × prix d'entrée
```

⚠️ **Toujours retirer le spread aller-retour estimé du R/R cible.** Pour SPY/QQQ : ~0.05% AR. Pour NVDA : ~0.10-0.15% AR.

## Workflow de chaque trade

```
1. Bernie détecte setup → log analysis/YYYY-MM-DD-HHMM-{symbol}.md
2. Bernie envoie WhatsApp:
   "📊 Setup [V2A/V2B] sur {SYMBOL} LONG
    Entrée: $X.XX  | SL: $X.XX  | TP: $X.XX
    Risque: 10€ | R/R: 1:X.X
    Raison: [pattern + contexte]
    ✅ Trader ? OUI / NON"
3. Quentin répond OUI/NON
4. Si OUI: Bernie ouvre via API + log trade dans trades/YYYY-MM-DD-{symbol}-NNN.md
5. Bernie monitore (checks adaptatifs)
6. SL/TP touché (serveur) OU sortie anticipée signalée
7. Bernie ferme via API (si sortie anticipée), met à jour le log
8. Debrief post-trade dans le log + update STATS.md + update PLAYBOOK.md si leçon
9. git commit + push
```

## Évolution de la stratégie

À chaque batch de **10 trades** : debrief approfondi.
- Si winrate < 35% sur 20 trades → revoir setup
- Si expectancy négative sur 20 trades → arrêt + nouvelle stratégie
- Si une condition d'entrée est régulièrement la cause d'échec → modifier ou retirer

Toute modif est **versionnée dans ce fichier** avec date.

## Versions

| Version | Date | Changement |
|---|---|---|
| V1 | 2026-05-29 | Création initiale crypto (abandonnée — API bloquée) |
| V2 | 2026-05-29 | Switch vers actions US / ETF (SPY, QQQ, NVDA) — 2 setups (pullback + breakout) |
