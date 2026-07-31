# ADR-0010 — Tenants multi-créateurs (agences) et autorisation par créateur

**Statut** : Accepté — révise une hypothèse d'[ADR-0009](0009-creator-twin-data-model-boundary.md)
**Date** : 2026-07-31
**Décideurs** : CTO / Architecture Creator OS — Sprint F2 (correction)

## Contexte

Sprint F2 a implémenté `Creator.tenant_id` comme **unique** : un tenant
ne pouvait avoir qu'un seul profil créateur. C'était une hypothèse
implicite, jamais un besoin produit vérifié. Le besoin réel : un tenant
peut être une **agence** qui gère plusieurs créateurs de contenu, et
doit pouvoir contrôler lequel de ces créateurs est actuellement
autorisé (actif) sous sa gestion.

Rien n'a été déployé à de vrais utilisateurs — cette hypothèse est
corrigée maintenant plutôt que retrofittée plus tard, conformément au
principe déjà appliqué pour Data Ownership (ADR-0003) : corriger tôt
coûte moins cher que corriger après coup.

## Décision

1. **`Creator.tenant_id` n'est plus unique.** Un tenant peut posséder
   plusieurs `Creator`.
2. **`Creator.is_authorized: bool`, défaut `True` à la création** —
   l'ajout d'un créateur par une agence est un acte intentionnel, il
   démarre actif. L'agence peut désactiver sans supprimer les données.
3. **Portée de `is_authorized`** : gate la **visibilité publique**
   (le créateur désautorisé disparaît de `/public/portfolios/{slug}`,
   même si le portfolio individuel reste marqué `is_published`), mais
   **ne bloque pas** la gestion interne (l'agence garde un accès
   lecture/écriture à un créateur désautorisé — utile pour mettre à
   jour son statut, consulter l'historique, ou le réautoriser).
4. **API en collection**, remplace le motif `/creators/me` de F2 :
   `POST /creators`, `GET /creators`, `GET/PATCH/DELETE /creators/{id}`.
5. **`Portfolio` gagne `creator_id`** (clé étrangère *interne* au
   service — autorisée, voir ADR-0009 : seules les FK **cross-service**
   sont interdites). Un portfolio appartient à un créateur précis, pas
   seulement au tenant. Routes déplacées sous
   `/creators/{creator_id}/portfolios/...`.
6. **Différé explicitement** : quel **utilisateur** précis d'une agence
   multi-personnes peut gérer quel créateur (délégation fine par
   collaborateur). Dépend d'un flow d'invitation multi-utilisateurs par
   tenant côté `identity`, qui n'existe pas encore (déjà noté comme
   différé en Sprint F1). Déclencheur explicite pour construire cette
   pièce : le jour où une agence a réellement plus d'un utilisateur
   connecté sur le même tenant. D'ici là, l'unique utilisateur du
   tenant gère tous ses créateurs.

## Alternatives envisagées

| Option | Rejetée car |
|---|---|
| Garder `tenant_id` unique, une agence = plusieurs tenants (un par créateur) | Casse l'isolation par tenant existante comme frontière naturelle « un client » ; complique la facturation future (Billing) qui devrait raisonner par agence, pas par créateur individuel |
| `is_authorized` bloque aussi l'accès interne de l'agence | Empêche de corriger ou réactiver un créateur désautorisé sans passer par un accès superadmin — inutilement restrictif pour un besoin de visibilité, pas de sécurité |
| Construire la délégation multi-utilisateurs maintenant | Aucune agence réelle avec plusieurs collaborateurs à ce stade ; le flow d'invitation identity est un morceau significatif à part entière (voir Sprint F1) — Cost First |

## Conséquences

**Positives**
- Le modèle correspond enfin au besoin produit réel plutôt qu'à une hypothèse de Sprint F2.
- La frontière tenant reste le bon niveau pour la facturation future (un abonnement par agence, pas par créateur).

**Négatives / à surveiller**
- Migration de schéma sur des données déjà écrites en Sprint F2 (aucune donnée réelle à ce stade — juste la contrainte `UNIQUE` à lever, pas de retrofit de données).
- Tant que la délégation multi-utilisateurs n'existe pas, un seul point de défaillance humain par agence (le compte unique) — acceptable au stade actuel, à revoir avant onboarding de vraies agences avec plusieurs employés.
