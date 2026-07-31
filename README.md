# Creator OS

**Operating System for Creators.** Pas un concurrent de Canva : le
portfolio est une interface, la plateforme est un système qui comprend un
créateur (Creator Twin), agit pour lui (AI Router, Connectors) et se
souvient de lui (Memory Engine).

> Statut : Sprint F0 (fondation) — voir [Roadmap](#roadmap)

## Stack

| Couche | Techno |
|---|---|
| Frontend | Next.js, React, TypeScript, TailwindCSS, shadcn/ui |
| Backend | FastAPI, Python |
| Données | PostgreSQL, Redis |
| Stockage | S3-compatible / MinIO + CDN |
| IA | Multi-provider (OpenAI, Anthropic, Gemini, Mistral, local) via AI Router — voir [ADR-0002](docs/adr/0002-ai-router-provider-agnostic.md) |

## Structure du monorepo

```
apps/            web (frontend créateur) · api (gateway) · admin (console interne)
services/        9 domaines métier isolés — voir docs/architecture/ARCHITECTURE.md
packages/        code partagé : ui, types, sdk, security, config
infrastructure/  docker, terraform, kubernetes
docs/            architecture, ADR, sécurité, documentation DSI
scripts/         outillage (validation de structure, etc.)
tests/
```

Décision d'architecture détaillée : [ADR-0001](docs/adr/0001-monorepo-enterprise.md).
Vue d'ensemble des 9 domaines : [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md).

## Démarrer en local

```bash
git clone https://github.com/veloufrance-officiel/creator-os.git
cd creator-os
cp .env.example .env
make up          # infrastructure locale : Postgres, Redis, MinIO
make install      # dépendances JS du monorepo (pnpm workspaces)
make structure-check   # valide la structure vs ADR-0001
```

`make up` ne lance que l'infrastructure de base. Aucun service applicatif
n'est encore implémenté à ce stade (Sprint F0 = fondation uniquement) —
voir Sprint F1 ci-dessous. `make help` liste toutes les commandes.

## Règle de travail

Aucun code n'est écrit sans, dans cet ordre :

1. Spécification
2. Décision d'architecture (ADR si structurant)
3. Tests prévus
4. Documentation à jour

Détail du process (PR, commits, issues) : [`CONTRIBUTING.md`](CONTRIBUTING.md).
Chaque sprint doit produire du code, des tests, de la documentation, et
une mise à jour du [`CHANGELOG.md`](CHANGELOG.md).

## Documentation

- [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md) — vision et 9 domaines
- [`docs/architecture/DOMAIN_MODEL.md`](docs/architecture/DOMAIN_MODEL.md) — migration des domaines V0 → V1
- [`docs/architecture/DATA_MODEL.md`](docs/architecture/DATA_MODEL.md) — modèle de données par service
- [`docs/architecture/ROADMAP.md`](docs/architecture/ROADMAP.md) — roadmap détaillée sprint par sprint
- [`docs/adr/`](docs/adr/) — décisions d'architecture ([template](docs/adr/0000-template.md))
- [`docs/architecture/v0/`](docs/architecture/v0/) — documentation V0 préservée
- [`SECURITY.md`](SECURITY.md) — politique de sécurité
- [`README_DSI.md`](README_DSI.md) — vision, gouvernance et risques pour parties prenantes non-techniques
- [`CONTRIBUTING.md`](CONTRIBUTING.md) · [`CHANGELOG.md`](CHANGELOG.md)

## Roadmap

- [x] **Sprint F0 — Foundation** : structure repo, documentation, CI/CD initial, Docker, sécurité documentée, tooling monorepo
- [x] **Sprint F1 — Identity Service** : register/login/refresh/logout, `/me`, RBAC, audit log, OAuth Google (web + natif) et Apple (natif, prépare le déploiement mobile) — un créateur peut créer un compte dans un environnement sécurisé
- [ ] **Sprint F2 — Creator Twin** (en cours) : prérequis RS256 + `packages/security` faits, `services/creator` à venir. Suivent : Media Engine, AI Core, Memory, Connectors, Billing, Quota

Détail : [`docs/architecture/ROADMAP.md`](docs/architecture/ROADMAP.md).

## Licence

Non définie à ce stade — voir [`NOTICE`](NOTICE) (placeholder, à valider
juridiquement avant toute ouverture externe du dépôt).
