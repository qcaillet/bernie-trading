    # R004 — R/R minimum 1:2

    **Sévérité :** `BLOCK`

    ## Quoi

    Le ratio (TP - entry) / (entry - SL) doit être ≥ 2.0 pour un long, ou (entry - TP) / (SL - entry) ≥ 2.0 pour un short. Au coût du spread près (le R/R **net** doit rester ≥ 2.0).

    ## Comment vérifier

    Avant proposal: calculer `rr_net = (abs(TP-entry) - spread_estimate) / (abs(entry-SL) + spread_estimate)`. Si < 2 → BLOCK.

    ## Exemples

    SPY entry=755, SL=750 (risque 5), TP=765 (gain 10) → R/R brut 2 → OK
SPY entry=755, SL=750, TP=764 → R/R 1.8 → BLOCK

    ## Référence

    Cette règle est listée dans `RULES.md`. Sa modification requiert un commit dédié + entrée dans `analysis/`.
