    # R001 — Stop-loss serveur obligatoire

    **Sévérité :** `BLOCK`

    ## Quoi

    Aucun ordre ne doit être ouvert via l'API sans `StopLossRate` dans le body. Si l'API ne supporte pas un SL serveur pour un instrument donné, on ne trade PAS cet instrument.

    ## Comment vérifier

    Check au moment de la construction du body POST market-open-orders. Si `StopLossRate` est null/absent → abort + raise EToroError.

    ## Exemples

    ✅ body inclut `StopLossRate: 750.10` → OK
❌ body sans `StopLossRate` → BLOCK

    ## Référence

    Cette règle est listée dans `RULES.md`. Sa modification requiert un commit dédié + entrée dans `analysis/`.
