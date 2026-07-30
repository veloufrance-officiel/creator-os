# ADR-0003 — Data Ownership & Privacy by Default

**Statut** : Accepté
**Date** : 2026-07-31
**Décideurs** : CTO / Architecture Creator OS

## Contexte

Les créateurs UGC confient à la plateforme des données sensibles :
identité, contenus, revenus de marque, contrats. Sur ce marché, la
confiance est un avantage concurrentiel face à des plateformes qui
exploitent la donnée par défaut. Retrofitter des droits d'export ou de
suppression sur un modèle de données déjà en production coûte largement
plus cher qu'une conception correcte dès le départ — sans compter le
risque de non-conformité RGPD dès le premier utilisateur européen.

## Décision

1. Tout service qui détient des données utilisateur (`identity`,
   `creator`, `media`, `billing`) doit exposer nativement : **export**,
   **suppression**, **migration**.
2. Toute donnée créée (portfolio, media kit, asset) est **privée par
   défaut**. La visibilité publique est un choix explicite, jamais un
   défaut.
3. Tout accès externe à une donnée privée passe par un **lien signé et
   expirable** (pas d'URL statique permanente vers un asset privé).
4. L'accès en lecture/écriture aux données est gouverné par RBAC
   (rôles + permissions), avec isolation stricte par tenant.

## Alternatives envisagées

| Option | Rejetée car |
|---|---|
| Opt-in privacy (privé seulement si activé) | Contraire au principe *Privacy By Default* et à l'exigence RGPD de *privacy by design* |
| Export/suppression traités comme fonctionnalité future | Coût de retrofit largement supérieur à une conception initiale correcte ; expose à un risque de conformité immédiat |

## Conséquences

**Positives**
- Conformité RGPD dès J0 (droit à l'export, à l'effacement, à la portabilité).
- Argument de confiance vis-à-vis des créateurs et des marques.

**Négatives / à surveiller**
- Chaque nouveau service manipulant des données utilisateur doit implémenter ces trois contrats dès sa création — à ajouter comme item obligatoire de la checklist de revue d'architecture (voir `docs/security/`).
- La gestion des liens signés nécessite une gestion de clés et d'expiration à construire tôt (dépendance `identity` ↔ `media`).
- La suppression doit être définie précisément par service (suppression logique vs physique, délais légaux de rétention pour la facturation notamment).
