# tests/

Stratégie de test — Sprint F0 (aucun code applicatif à tester à ce stade,
ce document fixe la règle pour les sprints suivants) :

- **Unitaire** — dans chaque `services/*` (pytest) et `packages/*` (vitest/jest), colocalisé avec le code, pas ici.
- **Contrat** — entre `apps/api` (gateway) et chaque service interne, pour éviter qu'un changement de schéma casse silencieusement un consommateur.
- **End-to-end** — parcours critiques uniquement (ex. inscription créateur, publication portfolio), ici dans `tests/e2e/` (à créer au moment du premier parcours testable).

Règle du projet : un service sans tests n'est pas considéré comme livré,
quel que soit l'état du code.
