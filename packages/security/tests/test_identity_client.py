"""Vraie paire de clés RSA + vrai JWT signé ; seule la récupération JWKS par URL est
simulée (même approche que services/identity/tests/test_oauth_native_token.py)."""
import time
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from creator_os_security import InvalidIdentityToken, verify_identity_token
from creator_os_security.identity_client import _jwks_clients


@pytest.fixture
def keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key, private_key.public_key()


@pytest.fixture(autouse=True)
def mock_jwks(monkeypatch, keypair):
    _, public_key = keypair
    monkeypatch.setattr(
        "jwt.PyJWKClient.get_signing_key_from_jwt",
        lambda self, token: SimpleNamespace(key=public_key),
    )
    _jwks_clients.clear()


def _make_token(private_key, **overrides) -> str:
    now = int(time.time())
    payload = {
        "sub": "user-123",
        "tenant_id": "tenant-456",
        "roles": ["owner"],
        "iat": now,
        "exp": now + 600,
        **overrides,
    }
    return jwt.encode(payload, private_key, algorithm="RS256")


def test_verifies_a_valid_token(keypair):
    private_key, _ = keypair
    token = _make_token(private_key)
    claims = verify_identity_token(token, identity_base_url="http://identity.internal")
    assert claims.user_id == "user-123"
    assert claims.tenant_id == "tenant-456"
    assert claims.roles == ["owner"]


def test_expired_token_rejected(keypair):
    private_key, _ = keypair
    token = _make_token(private_key, iat=int(time.time()) - 1000, exp=int(time.time()) - 100)
    with pytest.raises(InvalidIdentityToken):
        verify_identity_token(token, identity_base_url="http://identity.internal")


def test_token_missing_required_claim_rejected(keypair):
    private_key, _ = keypair
    now = int(time.time())
    payload = {"sub": "user-123", "iat": now, "exp": now + 600}  # pas de tenant_id
    token = jwt.encode(payload, private_key, algorithm="RS256")
    with pytest.raises(InvalidIdentityToken):
        verify_identity_token(token, identity_base_url="http://identity.internal")


def test_garbage_token_rejected():
    with pytest.raises(InvalidIdentityToken):
        verify_identity_token("not-a-jwt-at-all", identity_base_url="http://identity.internal")
