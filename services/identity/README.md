# services/identity

**Rôle** : Auth, IAM, RBAC, tenants, sessions, audit.

**Tables possédées** : `users`, `tenants`, `roles`, `permissions`,
`role_permissions`, `user_roles`, `sessions`, `audit_logs`,
`oauth_accounts` (modèle présent, aucune route — voir `SPEC.md`).

**Statut** : Sprint F1 complet — register (type de compte requis, ADR-0011),
login, refresh, logout, `/me`, `/tenant`, RBAC, audit log, OAuth Google
(web + natif) et Apple (natif). 38 tests, CI verte. Autres providers
OAuth, flow web Apple, délégation multi-utilisateurs et RLS Postgres
différés (voir `SPEC.md`).

**Spécification complète** : [`SPEC.md`](SPEC.md) — flux d'auth,
endpoints, décisions actées ([ADR-0004](../../docs/adr/0004-password-hashing-argon2id.md),
[ADR-0005](../../docs/adr/0005-jwt-hs256-then-rs256.md)).

## Lancer en local

```bash
cd services/identity
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
cp ../../.env.example ../../.env   # si pas déjà fait à la racine
alembic upgrade head               # nécessite Postgres, voir infrastructure/docker
uvicorn app.main:app --reload
```

## Tests

```bash
pytest -q       # SQLite en mémoire, aucune dépendance externe requise
ruff check app/ tests/ alembic/
```

Voir `docs/architecture/DATA_MODEL.md` et `SECURITY.md` à la racine du repo.
