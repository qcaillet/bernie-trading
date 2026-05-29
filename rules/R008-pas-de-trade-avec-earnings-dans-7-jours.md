    # R008 — Pas de trade avec earnings dans 7 jours

    **Sévérité :** `BLOCK`

    ## Quoi

    Pas de position sur un instrument dont l'entreprise (ou les top-5 holdings pour ETF) annonce ses earnings dans les 7 jours.

    ## Comment vérifier

    Skill `earnings-calendar` fournit prochain earnings par ticker. Si days_until_earnings < 7 → BLOCK ce ticker.

    ## Exemples

    NVDA earnings dans 5j → pas de trade NVDA jusqu'à 24h post-earnings.
SPY top-5: AAPL earnings dans 5j → BLOCK SPY ce jour-là.

    ## Référence

    Cette règle est listée dans `RULES.md`. Sa modification requiert un commit dédié + entrée dans `analysis/`.
