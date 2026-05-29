# Playbook

> Ce fichier est la mémoire active de Bernie. Avant chaque décision, Bernie relit ce playbook pour s'imprégner des leçons accumulées.

## Patterns qui MARCHENT

_(à remplir au fur et à mesure)_

## Patterns qui NE MARCHENT PAS

_(à remplir au fur et à mesure)_

## Biais détectés chez Bernie

_(à remplir au fur et à mesure)_

## Biais détectés chez Quentin

- ⚠️ Tendance à attendre "que ce soit sûr" avant d'entrer (procrastination liée au profil psy) → risque de rater les setups
- ⚠️ Peut être tenté de couper trop vite par peur de rendre les gains
- _(à compléter au fil des trades)_

## Règles ajoutées suite à des erreurs

_(format : Date | Trade ID | Erreur | Règle ajoutée)_

| Date | Trade | Erreur observée | Règle ajoutée |
|---|---|---|---|

## Apprentissages génériques

_(format libre, idées qu'on veut garder en tête)_

### 2026-05-29 — Pièges API eToro (validation end-to-end SPY OK)

- **Close position** : le body **doit** contenir `{"InstrumentId": <id>}`. La doc dit `{"UnitsToDeduct": null}`, c'est faux/incomplet, ça renvoie HTTP 400.
- **orderID ≠ positionID** : après un open, faire `GET /trading/info/demo/orders/{orderId}` pour récupérer le `positionID` réel (nécessaire pour le close).
- **`isExchangeOpen`** est buggué, ne pas s'y fier. Utiliser `isCurrentlyTradable` + `isBuyEnabled`.
- **statusID** : 1=pending, 3=executed, 4=rejected.
- **Coût minimum** sur SPY (ouverture+fermeture immédiate, spread aller-retour) : ~0.3% du montant. À prendre en compte dans le R/R cible.
- Réf complète : `analysis/2026-05-29-1422-etoro-api-actions-OK.md`

### 2026-05-29 — Tester la plomberie AVANT de cimenter la stratégie

Le 1er test end-to-end de l'API eToro a révélé que **la crypto est bloquée** à l'auto-trading via API publique (errorCode 759). Si on avait passé des semaines à peaufiner la stratégie crypto avant ce test, on aurait perdu un temps fou.

**Règle générique :** avant de figer une stratégie sur un actif/marché, **toujours valider que toute la chaîne technique (data + exécution + monitoring + fermeture) fonctionne sur cet actif spécifique**, avec un trade min en démo. Réf : `analysis/2026-05-29-1418-etoro-api-crypto-blocked.md`.
