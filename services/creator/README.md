# services/creator

**Rôle** : Creator Twin — profil créateur enrichi (une seule table
`creators`, voir [ADR-0009](../../docs/adr/0009-creator-twin-data-model-boundary.md)),
portfolios et blocs (le portfolio affiché reste une vue dans `apps/web`,
ce service en détient la structure et l'expose publiquement par slug).

**Tables possédées** : `creators`, `portfolios`, `portfolio_blocks`.
Aucune FK vers les tables `identity` (ADR-0009).

**Statut** : Sprint F2 — implémenté et testé (profil, portfolios, blocs,
publication, isolation tenant). 17 tests. Bio IA et upload média réels
différés (voir `SPEC.md`).

**Spécification complète** : [`SPEC.md`](SPEC.md).

## Lancer en local

```bash
cd services/creator
python3 -m venv .venv && . .venv/bin/activate
pip install -e ../../packages/security   # dépendance locale, dans cet ordre (voir CI)
pip install -e ".[dev]"
cp ../../.env.example ../../.env
alembic upgrade head                     # nécessite Postgres, voir infrastructure/docker
uvicorn app.main:app --reload --port 8001
```

## Tests

```bash
pytest -q
ruff check app/ tests/
```
