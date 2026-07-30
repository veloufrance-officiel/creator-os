# Security Policy — Creator OS

Ce document traduit les principes de la *Creator Constitution* en mesures
concrètes. Il évolue à chaque sprint qui touche à l'identité, aux données
ou à l'IA.

## Signalement d'une vulnérabilité

Toute vulnérabilité suspectée doit être signalée via une issue privée
GitHub Security Advisory sur ce dépôt (jamais une issue publique). Un
canal de contact dédié (email sécurité) sera publié ici avant l'ouverture
de la plateforme à des utilisateurs externes — non défini à ce stade
(Sprint F0), à traiter avant la fin de Sprint F1.

## IAM & RBAC

Porté par `services/identity` (voir `docs/architecture/DATA_MODEL.md`).

- Modèle : `users` → `user_roles` → `roles` → `role_permissions` → `permissions`.
- Aucune permission implicite : tout accès non explicitement accordé est refusé par défaut (deny by default).
- Les sessions sont propres à un tenant ; un token émis pour un tenant n'est jamais valide pour un autre.

## Isolation tenant

Une agence ou une marque (tenant) ne doit jamais pouvoir accéder, même par
erreur applicative, aux données d'un autre tenant. Deux niveaux de
défense :

1. Filtrage applicatif systématique par `tenant_id` dans chaque requête.
2. Row-Level Security PostgreSQL en défense en profondeur, activée au
   moment de l'implémentation de `services/identity` (Sprint F1).

## Chiffrement

- **En transit** : TLS partout, y compris en interne entre services une fois l'architecture déployée sur Kubernetes (`infrastructure/kubernetes`).
- **Au repos** : chiffrement natif PostgreSQL/S3-compatible (MinIO) activé au niveau infrastructure. Les secrets (tokens OAuth des connecteurs, clés API) ne sont jamais stockés en clair — voir Gestion des secrets ci-dessous.

## Audit logging

Toute action sensible (connexion, changement de permission, export de
données, suppression de compte, décision de l'AI Router) est journalisée
dans `audit_logs` (`services/identity`). Le journal d'audit est
lui-même en lecture seule pour tous les rôles sauf un rôle d'audit dédié.

## Gestion des secrets

- Aucun secret en dur dans le code ni dans les fichiers versionnés (voir `.gitignore`).
- Variables d'environnement en local (`.env`, non commité), gestionnaire de secrets managé en production (à choisir au moment du sprint infrastructure — non tranché à ce stade, voir `infrastructure/terraform/README.md`).

## Droits sur les données (RGPD / Data Ownership)

Implémente [ADR-0003](docs/adr/0003-data-ownership-privacy-by-default.md).
Chaque service détenant des données utilisateur (`identity`, `creator`,
`media`, `billing`) doit exposer :

- **Export** — l'utilisateur peut obtenir une copie structurée de ses données.
- **Suppression** — logique puis physique, sous réserve des délais légaux de rétention (facturation notamment).
- **Migration** — portabilité vers un autre outil.

Toute donnée est **privée par défaut**. Le partage externe passe
exclusivement par des liens signés et expirables (`signed_urls`,
`services/media`).

## AI Governance

Implémente [ADR-0002](docs/adr/0002-ai-router-provider-agnostic.md).
Chaque décision de l'AI Router (quel modèle, pourquoi) est journalisée
dans `ai_router_decisions` et doit rester **explicable** a posteriori —
ce n'est pas optionnel, c'est un principe fondateur du projet.

## Sécurité de la chaîne de dépendances

- CI (`\.github/workflows/ci.yml`) exécute un audit de dépendances (`npm audit` / `pip-audit` ou équivalent) à chaque PR — à activer concrètement dès le premier service codé (Sprint F1), le skeleton CI actuel prévoit l'emplacement.
- Dependabot (ou équivalent) à activer sur le dépôt dès que du code applicatif existe.

## Feuille de route conformité

| Étape | Statut |
|---|---|
| RGPD (export/suppression/migration natifs) | Conçu (ADR-0003), à implémenter Sprint F1+ |
| Isolation tenant | Conçu, à implémenter Sprint F1 |
| Audit logging | Conçu, à implémenter Sprint F1 |
| Certification externe (type SOC 2) | Non engagée — à réévaluer une fois des clients Enterprise identifiés |

## Ce document n'est pas figé

Il doit être mis à jour à chaque sprint qui introduit une nouvelle surface
de données ou d'accès — conformément à la règle de travail du projet
(*pas de code sans documentation à jour*).
