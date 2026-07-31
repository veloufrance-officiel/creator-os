# packages/security

Vérification partagée des tokens émis par `services/identity` — voir
[ADR-0008](../../docs/adr/0008-rs256-migration-shared-security-package.md).
Tout service qui doit authentifier un appel via un token identity
importe ce package plutôt que de réimplémenter sa propre vérification
JWKS.

**Statut** : implémenté, 4 tests. `services/creator` (Sprint F2) est le
premier consommateur.

```python
from creator_os_security import verify_identity_token, InvalidIdentityToken

try:
    claims = verify_identity_token(token, identity_base_url="http://identity:8000")
except InvalidIdentityToken:
    ...  # 401
```

## Tests

```bash
cd packages/security
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```
