# Creator OS — Roadmap

Complète [`ARCHITECTURE.md`](ARCHITECTURE.md). Statut détaillé sprint par
sprint — la vue rapide est dans le `README.md` racine, celle-ci est la
source de vérité.

## Sprint F0 — Foundation ✅

- [x] Repository structuré (`apps/`, `services/`, `packages/`, `infrastructure/`, `docs/`, `tests/`)
- [x] Documentation créée (README, README_DSI, SECURITY, ARCHITECTURE, DOMAIN_MODEL, DATA_MODEL, 3 ADR, CONTRIBUTING, CHANGELOG)
- [x] Documentation V0 préservée (`docs/architecture/v0/`)
- [x] CI/CD initial (validation de structure, markdown lint, dependency review — jobs applicatifs désactivés tant qu'il n'y a pas de code)
- [x] Environnement Docker local (Postgres, Redis, MinIO)
- [x] Sécurité documentée (`SECURITY.md`)
- [x] Tooling monorepo (pnpm workspaces, Turborepo, Makefile, script de validation de structure)

## Sprint F1 — Identity Service ✅

Objectif : un créateur peut créer un compte dans un environnement sécurisé.

- [x] Spécification (`services/identity/SPEC.md`) avant le code
- [x] Décisions actées : [ADR-0004](../adr/0004-password-hashing-argon2id.md) (Argon2id), [ADR-0005](../adr/0005-jwt-hs256-then-rs256.md) (JWT HS256 → RS256), [ADR-0006](../adr/0006-oauth-provider-abstraction-account-linking.md) (OAuth)
- [x] User, Tenant, Role, Permission, Session, Audit Log — implémentés et testés
- [x] OAuth Google — abstraction provider-agnostique, politique de rattachement de compte (ADR-0006)
- [x] Migrations Alembic (2 : schéma initial + mot de passe nullable pour comptes OAuth-only)
- [x] 21 tests (SQLite en mémoire), CI `identity-service` (ruff + pytest) verte
- [ ] Row-Level Security PostgreSQL — isolation tenant en défense en profondeur (filtrage applicatif en place ; RLS reporté, pas bloquant)
- [ ] Autres providers OAuth (GitHub, etc.) — abstraction prête, ajoutés à la demande produit

## Sprint F2 — Creator Twin (prochain, dans l'ordre)

- Media Engine (`services/media`)
- AI Core (`services/ai`) — voir ADR-0002
- Memory Engine (`services/memory`)
- Connectors (`services/connector`)
- Billing (`services/billing`) & Quota (`services/quota`)
- Décision sur `Brand` / `Campaign` (voir `DOMAIN_MODEL.md`)

## Non planifié / décisions ouvertes

- Choix du cloud provider (`infrastructure/terraform`)
- Choix définitif de la stack de paiement (Stripe pressenti, non tranché)
- Canal de signalement de vulnérabilité externe (voir `SECURITY.md`)
- Mentions légales définitives (`NOTICE` est un placeholder à valider juridiquement)
