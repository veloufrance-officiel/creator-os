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

## Sprint F1 — Identity Service (prochain)

Objectif : un créateur peut créer un compte dans un environnement sécurisé.

Fonctions : User, Tenant, Role, Permission, Session, OAuth, Audit Log.

Prérequis avant de coder (règle de travail, voir `CONTRIBUTING.md`) :
spécification du service, schéma de données détaillé (au-delà du niveau
`DATA_MODEL.md`), tests prévus.

## Sprints suivants (ordre non figé)

- Creator Twin (`services/creator`)
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
