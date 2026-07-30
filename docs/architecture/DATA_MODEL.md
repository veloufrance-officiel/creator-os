# Creator OS — Modèle de données V1

Enrichit `docs/architecture/v0/DATABASE.md`. Principe directeur : **chaque
table appartient à un seul service** (pas d'accès direct cross-service à
la base d'un autre domaine — tout passe par l'API interne de ce service).
Ce document liste les tables par service et leur rôle ; le schéma détaillé
(colonnes, contraintes, migrations) est produit au moment du sprint
d'implémentation de chaque service, pas avant.

## `services/identity`

| Table | Rôle |
|---|---|
| `users` | Compte de connexion (reprend `users` V0) |
| `tenants` | Isolation multi-tenant (agence gérant plusieurs créateurs, marque) |
| `roles`, `permissions`, `role_permissions`, `user_roles` | RBAC |
| `sessions` | Sessions actives |
| `oauth_accounts` | Comptes OAuth liés (login social, distinct des connecteurs réseaux sociaux métier) |
| `audit_logs` | Journal d'audit — obligatoire (principe Security First) |

## `services/creator`

| Table | Rôle |
|---|---|
| `creators` | Reprend `creators` V0 |
| `creator_twins` | Représentation enrichie du créateur (au-delà du simple profil CRUD) |
| `portfolios`, `portfolio_blocks` | Reprend V0 — config de présentation, consommée par `apps/web` |

## `services/media`

| Table | Rôle |
|---|---|
| `assets` | Reprend `assets` V0 |
| `media_kits` | Formalise le domaine MediaKit (V0, jamais spécifié) |
| `signed_urls` | Accès temporaire — implémente ADR-0003 (liens signés/expirables) |

## `services/ai`

| Table | Rôle |
|---|---|
| `ai_requests` | Chaque appel IA, entrant |
| `ai_router_decisions` | Provider choisi + raison (coût/qualité/contexte/quota) — implémente l'exigence d'explicabilité (principe AI Governance) |

## `services/memory`

| Table | Rôle |
|---|---|
| `memory_entries` | Remplace/étend le domaine `AIMemory` V0, mémoire par créateur |

## `services/connector`

| Table | Rôle |
|---|---|
| `connector_accounts` | Comptes externes liés (Instagram, TikTok, Canva…) |
| `connector_sync_logs` | Historique des synchronisations |

## `services/billing`

| Table | Rôle |
|---|---|
| `subscriptions` | Reprend `subscriptions` V0 |
| `invoices` | Facturation détaillée |

## `services/quota`

| Table | Rôle |
|---|---|
| `quota_limits` | Limites par tenant/plan |
| `quota_usage` | Consommation — consulté par l'AI Router avant chaque appel (ADR-0002) |

## `services/analytics`

| Table | Rôle |
|---|---|
| `analytics_events` | Reprend le domaine `Analytics` V0, événements bruts |

## `services/security`

Pas de table applicative propre à ce stade : rôle transverse (politiques,
revue, `packages/security`). À réévaluer si un besoin de stockage de
policies dynamiques apparaît.

## Domaines V0 non tranchés

`Brand` et `Campaign` (cités dans `docs/architecture/v0/ARCHITECTURE.md`
sans spécification) n'ont pas de table attribuée : décision explicite en
attente, voir `docs/architecture/DOMAIN_MODEL.md`.
