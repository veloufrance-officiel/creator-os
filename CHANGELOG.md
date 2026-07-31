# Changelog

Toutes les évolutions notables de Creator OS sont documentées ici.
Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).

## [Non publié]

### Ajouté — Sprint F2 (prérequis)

- Migration RS256 ([ADR-0008](docs/adr/0008-rs256-migration-shared-security-package.md)) : `services/identity` signe désormais en RS256, expose `GET /.well-known/jwks.json`. Déclencheur ADR-0005 atteint (second service, `creator`, doit vérifier les tokens identity).
- `packages/security` : package Python partagé (`creator_os_security`), vérification de token identity par JWKS, 4 tests. Premier consommateur : `services/creator` (à venir).
- Secret distinct (`OAUTH_STATE_SECRET`) pour le state OAuth anti-CSRF, désormais découplé des clés de signature des access tokens.
- CI : job `packages-security` (ruff + pytest) ajouté.
- 34 tests au total : 30 dans `services/identity`, 4 dans `packages/security`.

### Ajouté — Sprint F1 (Identity Service, complet)

- `services/identity` : register, login, refresh (rotation de session), logout, `/me`, `/audit-logs`
- OAuth Google (`/auth/oauth/google/authorize`, `/callback`) : abstraction provider-agnostique, politique de rattachement de compte
- Sign-in natif mobile + web SDK (`POST /auth/oauth/{google|apple}/token`) : vérification d'ID token OIDC, prépare le déploiement mobile (iOS/Android) en plus du web — [ADR-0007](docs/adr/0007-oidc-id-token-verification-multiplatform.md)
- Sign in with Apple (natif) — requis par Apple dès qu'un autre login social est proposé sur iOS
- Support multi-audience (un client ID par plateforme) pour Google et Apple
- RBAC fonctionnel de bout en bout (deny by default), audit log sur les événements d'auth
- [ADR-0004](docs/adr/0004-password-hashing-argon2id.md) (Argon2id), [ADR-0005](docs/adr/0005-jwt-hs256-then-rs256.md) (JWT HS256 → RS256), [ADR-0006](docs/adr/0006-oauth-provider-abstraction-account-linking.md) (rattachement de compte), [ADR-0007](docs/adr/0007-oidc-id-token-verification-multiplatform.md) (multi-plateforme)
- 2 migrations Alembic (schéma initial + mot de passe nullable)
- 27 tests (SQLite en mémoire), lint ruff propre, CI `identity-service` verte

### Différé (voir `services/identity/SPEC.md`)

- Flow redirection web pour Apple (natif fait, web différé)
- Autres providers OAuth (abstraction prête, ajout à la demande)
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
