    # R005 — Pas de moyenne à la baisse

    **Sévérité :** `BLOCK`

    ## Quoi

    INTERDIT d'augmenter une position perdante en espérant qu'elle remonte. C'est la règle qui détruit les comptes.

    ## Comment vérifier

    Si une position est ouverte sur un instrument et qu'on identifie un signal d'achat sur ce MÊME instrument : si la position est en perte (mark > entry pour short, mark < entry pour long), on N'AUGMENTE PAS. On peut ouvrir une position indépendante uniquement si la 1ère est en profit ET que c'est un setup différent.

    ## Exemples

    Long SPY @755, prix actuel 752 (perte) → NOUVELLE position SPY ? BLOCK
Long SPY @755, prix 760 (profit), nouveau setup pullback différent → autorisé (avec R009 respecté)

    ## Référence

    Cette règle est listée dans `RULES.md`. Sa modification requiert un commit dédié + entrée dans `analysis/`.
