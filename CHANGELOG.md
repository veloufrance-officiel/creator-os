# Changelog

Toutes les évolutions notables de Creator OS sont documentées ici.
Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).

## [Non publié]

### Ajouté — Sprint F1 (Identity Service, cœur)

- `services/identity` : register, login, refresh (rotation de session), logout, `/me`, `/audit-logs`
- RBAC fonctionnel de bout en bout (deny by default), audit log sur les événements d'auth
- [ADR-0004](docs/adr/0004-password-hashing-argon2id.md) (Argon2id) et [ADR-0005](docs/adr/0005-jwt-hs256-then-rs256.md) (JWT HS256 → RS256)
- Migration Alembic initiale (9 tables, cible Postgres)
- 13 tests (SQLite en mémoire), lint ruff propre
- CI : job `identity-service` activé (ruff + pytest)

### Différé (voir `services/identity/SPEC.md`)

- OAuth (dépend d'un choix de provider externe)
- Row-Level Security PostgreSQL (isolation tenant en défense en profondeur)

## [0.1.0] — Sprint F0 — 2026-07-31

### Ajouté

- Structure monorepo Enterprise (`apps/`, `services/`, `packages/`, `infrastructure/`, `docs/`, `tests/`) — [ADR-0001](docs/adr/0001-monorepo-enterprise.md)
- Documentation : `README.md`, `README_DSI.md`, `SECURITY.md`, `CONTRIBUTING.md`
- Architecture : `docs/architecture/ARCHITECTURE.md`, `DOMAIN_MODEL.md`, `DATA_MODEL.md`, `ROADMAP.md`
- Décisions d'architecture : ADR-0001 (monorepo), ADR-0002 (AI Router agnostique), ADR-0003 (Data Ownership & Privacy by Default)
- Documentation V0 préservée dans `docs/architecture/v0/`
- CI/CD initial : validation de structure, markdown lint, dependency review (jobs applicatifs présents mais désactivés tant qu'aucun service n'est codé)
- Environnement Docker local : PostgreSQL, Redis, MinIO
- Tooling monorepo : pnpm workspaces, Turborepo, Makefile, script `scripts/check_structure.py`
- Templates GitHub : PR, issues (bug/fonctionnalité au format formulaire), CODEOWNERS

### Non inclus (volontairement)

Aucun service applicatif. Sprint F0 est une fondation, pas un MVP —
voir [`docs/architecture/ROADMAP.md`](docs/architecture/ROADMAP.md).
