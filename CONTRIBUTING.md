# Contribuer à Creator OS

## Règle de travail

Aucun code n'est écrit sans, dans cet ordre :

1. **Spécification** — ce que fait le changement, ce qu'il ne fait pas
2. **Décision d'architecture** — un ADR si le changement est structurant (nouvelle dépendance entre services, changement de frontière de domaine, impact sécurité/RGPD). Partir de [`docs/adr/0000-template.md`](docs/adr/0000-template.md)
3. **Tests prévus** — avant le code, pas après
4. **Documentation à jour** — le README du service concerné, et `docs/architecture/` si la structure change

Un service livré sans tests n'est pas considéré comme terminé, quel que
soit l'état du code (voir `tests/README.md`).

## Process de PR

1. Utiliser le template de PR (checklist spec/ADR/tests/doc).
2. La CI doit passer : validation de structure (`scripts/check_structure.py`), markdown lint, dependency review, puis lint/tests du service concerné une fois activés.
3. Revue par le CODEOWNER du chemin concerné (`.github/CODEOWNERS`) — automatique sur `services/identity`, `services/security`, `packages/security`, `infrastructure/`, `docs/adr/`.

## Convention de commits

Préfixes type *Conventional Commits* : `chore:`, `feat:`, `fix:`,
`docs:`, `test:`, `refactor:`. Exemple du premier commit du repo :
`chore: initialize Creator OS enterprise monorepo foundation`.

## Ouvrir une issue

- Bug → template *Bug* (`.github/ISSUE_TEMPLATE/bug_report.yml`)
- Fonctionnalité → template *Fonctionnalité* (`.github/ISSUE_TEMPLATE/feature_request.yml`), qui inclut une case à cocher si un ADR est probablement nécessaire
- Question d'architecture qui n'est ni un bug ni une fonctionnalité → GitHub Discussions (voir `.github/ISSUE_TEMPLATE/config.yml`)

## Environnement local

```bash
cp .env.example .env        # puis adapter si besoin
make up                     # Postgres, Redis, MinIO
make install                # dépendances JS du monorepo (pnpm)
make structure-check        # valide la structure vs ADR-0001
make help                   # liste des commandes disponibles
```

## Principes non négociables

Toute contribution doit rester compatible avec la *Creator Constitution*
(voir `README_DSI.md`) : Data Ownership, Privacy By Default, AI
Governance, Cost First, Provider Agnostic, Security First. Une PR qui
enfreint l'un de ces principes n'est pas mergeable, même si elle « marche ».
