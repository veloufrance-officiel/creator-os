# ADR-0001 — Architecture Monorepo Enterprise

**Statut** : Accepté
**Date** : 2026-07-31
**Décideurs** : CTO / Architecture Creator OS

## Contexte

Creator OS passe d'un portfolio-builder mono-domaine (V0) à une plateforme
multi-domaines : Identity, Creator Twin, Media Engine, AI Core, Memory,
Connectors, Billing, Quota, Security. Ces domaines partagent des types,
des contrats d'API, des composants UI et des règles de sécurité communes
(RBAC, contexte tenant, quotas).

Un existant en polyrepo (un dépôt par service) imposerait de dupliquer ou
de publier séparément ces éléments partagés, avec un coût de synchronisation
élevé pour une équipe qui démarre.

## Décision

Option A — **monorepo complet**, structuré en cinq zones :

- `apps/` — interfaces (web créateur, api gateway, admin interne)
- `services/` — domaines métier isolés (un dossier = un service)
- `packages/` — code partagé (ui, types, sdk, security, config)
- `infrastructure/` — Docker, Terraform, Kubernetes
- `docs/` — architecture, ADR, sécurité, documentation DSI

## Alternatives envisagées

| Option | Rejetée car |
|---|---|
| Polyrepo (1 repo / service) | Duplication des types et contrats, CI cross-repo complexe, overhead de synchro disproportionné à ce stade |
| Hybride (frontend séparé du reste) | Casse l'atomicité des PR qui touchent à la fois contrat API et UI, double historique Git |

## Conséquences

**Positives**
- Cohérence des types partagés (`packages/types`, `packages/sdk`) — un seul endroit à faire évoluer.
- Un PR peut modifier plusieurs services de façon atomique et reviewée ensemble.
- CI/CD unifiée, un seul pipeline à maintenir au démarrage.

**Négatives / à surveiller**
- Le repo grossit avec le temps → la CI doit filtrer par chemin (path filtering) pour ne pas tout rebuild à chaque PR.
- Le monorepo n'empêche pas un déploiement indépendant par service (chaque `services/*` a son propre Dockerfile et manifeste Kubernetes) — mais ça doit rester une règle explicite, pas un hasard.
- Si un service doit un jour être extrait dans son propre repo (ex. scaling d'équipe dédiée), prévoir que l'historique Git ne suit pas automatiquement — décision à documenter dans un futur ADR le cas échéant.
