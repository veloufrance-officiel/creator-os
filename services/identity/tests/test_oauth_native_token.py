"""Tests du flow ID token natif (ADR-0007). On génère une vraie paire de clés de
test et un vrai JWT signé RS256 : seule la récupération des clés publiques par URL
(PyJWKClient) est simulée — la vérification de signature/iss/aud est bien réelle."""
import time
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app import config
from app.oauth import oidc


@pytest.fixture(scope="module")
def test_keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key, private_key.public_key()


def _make_id_token(private_key, *, issuer, audience, subject, email, email_verified) -> str:
    now = int(time.time())
    payload = {
        "iss": issuer,
        "aud": audience,
        "sub": subject,
        "email": email,
        "email_verified": email_verified,
        "iat": now,
        "exp": now + 600,
    }
    return jwt.encode(payload, private_key, algorithm="RS256")


@pytest.fixture
def mock_jwks(monkeypatch, test_keypair):
    _, public_key = test_keypair

    def fake_get_signing_key_from_jwt(self, token):
        return SimpleNamespace(key=public_key)

    monkeypatch.setattr(
        "jwt.PyJWKClient.get_signing_key_from_jwt", fake_get_signing_key_from_jwt
    )
    oidc._jwks_clients.clear()  # évite un client mis en cache d'un test précédent


async def test_google_token_signin_creates_account(client, mock_jwks, test_keypair, monkeypatch):
    monkeypatch.setattr(config.settings, "google_oauth_client_ids", "web-client-id")
    private_key, _ = test_keypair
    token = _make_id_token(
        private_key,
        issuer="https://accounts.google.com",
        audience="web-client-id",
        subject="google-native-uid",
        email="native-google@creator-os.dev",
        email_verified=True,
    )

    resp = await client.post("/auth/oauth/google/token", json={"id_token": token})
    assert resp.status_code == 200
    me = await client.get("/me", headers={"Authorization": f"Bearer {resp.json()['access_token']}"})
    assert me.json()["email"] == "native-google@creator-os.dev"


async def test_apple_token_signin_creates_account(client, mock_jwks, test_keypair, monkeypatch):
    monkeypatch.setattr(config.settings, "apple_client_ids", "com.creatoros.app")
    private_key, _ = test_keypair
    token = _make_id_token(
        private_key,
        issuer="https://appleid.apple.com",
        audience="com.creatoros.app",
        subject="apple-native-uid",
        email="native-apple@creator-os.dev",
        email_verified="true",  # quirk Apple : chaîne, pas booléen (ADR-0007)
    )

    resp = await client.post("/auth/oauth/apple/token", json={"id_token": token})
    assert resp.status_code == 200
    me = await client.get("/me", headers={"Authorization": f"Bearer {resp.json()['access_token']}"})
    assert me.json()["email"] == "native-apple@creator-os.dev"


async def test_token_signin_wrong_audience_rejected(client, mock_jwks, test_keypair, monkeypatch):
    monkeypatch.setattr(config.settings, "google_oauth_client_ids", "web-client-id")
    private_key, _ = test_keypair
    token = _make_id_token(
        private_key,
        issuer="https://accounts.google.com",
        audience="a-different-client-id",  # n'est pas dans la liste autorisée
        subject="uid",
        email="x@creator-os.dev",
        email_verified=True,
    )

    resp = await client.post("/auth/oauth/google/token", json={"id_token": token})
    assert resp.status_code == 401


async def test_token_signin_wrong_issuer_rejected(client, mock_jwks, test_keypair, monkeypatch):
    monkeypatch.setattr(config.settings, "google_oauth_client_ids", "web-client-id")
    private_key, _ = test_keypair
    token = _make_id_token(
        private_key,
        issuer="https://not-google.evil",
        audience="web-client-id",
        subject="uid",
        email="x@creator-os.dev",
        email_verified=True,
    )

    resp = await client.post("/auth/oauth/google/token", json={"id_token": token})
    assert resp.status_code == 401


async def test_token_signin_accepts_any_configured_audience(client, mock_jwks, test_keypair, monkeypatch):
    """Multi-plateforme (ADR-0007) : un token émis pour l'app iOS doit passer même si
    web-client-id est listé en premier."""
    monkeypatch.setattr(config.settings, "google_oauth_client_ids", "web-client-id,ios-client-id,android-client-id")
    private_key, _ = test_keypair
    token = _make_id_token(
        private_key,
        issuer="https://accounts.google.com",
        audience="ios-client-id",
        subject="uid-ios",
        email="ios-user@creator-os.dev",
        email_verified=True,
    )

    resp = await client.post("/auth/oauth/google/token", json={"id_token": token})
    assert resp.status_code == 200


async def test_unknown_token_provider_returns_404(client):
    resp = await client.post("/auth/oauth/facebook/token", json={"id_token": "whatever"})
    assert resp.status_code == 404
