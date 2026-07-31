# services/creator

**Rôle** : Creator Twin — profil créateur enrichi, portfolios et blocs.
Un tenant peut être un créateur solo ou une **agence gérant plusieurs
créateurs** avec autorisation par créateur (voir
[ADR-0009](../../docs/adr/0009-creator-twin-data-model-boundary.md) et
[ADR-0010](../../docs/adr/0010-multi-creator-agency-tenants.md)).

**Tables possédées** : `creators`, `portfolios`, `portfolio_blocks`.
Aucune FK vers les tables `identity` (ADR-0009).

**Statut** : Sprint F2 — implémenté et testé (créateurs multiples par
tenant, autorisation, portfolios, blocs, publication, isolation tenant).
24 tests. Bio IA, upload média réel, et délégation fine multi-utilisateurs
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
