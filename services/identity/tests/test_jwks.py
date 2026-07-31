"""Vérifie ADR-0008 : identity signe en RS256, expose sa JWKS, et un token signé
peut être vérifié à partir de cette JWKS seule (comme le fera packages/security
depuis un autre service — pas d'accès à la clé privée nécessaire)."""
import json
import uuid

import jwt
from jwt.algorithms import RSAAlgorithm

from app import security


async def test_jwks_endpoint_returns_well_formed_jwks(client):
    resp = await client.get("/.well-known/jwks.json")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["keys"]) == 1
    key = body["keys"][0]
    assert key["kty"] == "RSA"
    assert key["alg"] == "RS256"
    assert key["use"] == "sig"
    assert "n" in key and "e" in key


async def test_access_token_is_rs256_and_carries_kid():
    token = security.create_access_token(user_id=uuid.uuid4(), tenant_id=uuid.uuid4(), roles=["owner"])
    header = jwt.get_unverified_header(token)
    assert header["alg"] == "RS256"
    assert header["kid"] == security.settings.jwt_key_id


async def test_token_verifiable_from_jwks_alone_like_another_service_would(client, registered_user_payload):
    """Reproduit ce que fera packages/security depuis services/creator : récupérer la
    JWKS publiée, pas la clé privée, et vérifier un token émis par identity."""
    register_resp = await client.post("/auth/register", json=registered_user_payload)
    access_token = register_resp.json()["access_token"]

    jwks_body = (await client.get("/.well-known/jwks.json")).json()
    signing_key = RSAAlgorithm.from_jwk(json.dumps(jwks_body["keys"][0]))

    claims = jwt.decode(access_token, signing_key, algorithms=["RS256"])
    assert "sub" in claims
    assert claims["roles"] == ["owner"]
