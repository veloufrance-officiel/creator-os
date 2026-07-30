# Changelog

Toutes les évolutions notables de Creator OS sont documentées ici.
Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).

## [Non publié]

Rien pour l'instant — Sprint F1 (Identity Service) à venir.

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
