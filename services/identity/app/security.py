"""Hachage de mot de passe (ADR-0004) et JWT (ADR-0005, migré RS256 par ADR-0008)."""
import base64
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from hashlib import sha256

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.config import settings

_hasher = PasswordHasher()


def _load_or_generate_keypair():
    if settings.jwt_private_key_pem and settings.jwt_public_key_pem:
        private_key = serialization.load_pem_private_key(settings.jwt_private_key_pem.encode(), password=None)
        public_key = serialization.load_pem_public_key(settings.jwt_public_key_pem.encode())
        return private_key, public_key

    # Dev uniquement (voir ADR-0008) : paire éphémère, non persistante.
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key, private_key.public_key()


_private_key, _public_key = _load_or_generate_keypair()


def _b64url_uint(value: int) -> str:
    length = (value.bit_length() + 7) // 8
    return base64.urlsafe_b64encode(value.to_bytes(length, "big")).rstrip(b"=").decode()


def get_jwks() -> dict:
    """Format JWKS standard — voir GET /.well-known/jwks.json et ADR-0008."""
    numbers = _public_key.public_numbers()
    return {
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "alg": "RS256",
                "kid": settings.jwt_key_id,
                "n": _b64url_uint(numbers.n),
                "e": _b64url_uint(numbers.e),
            }
        ]
    }


def hash_password(raw: str) -> str:
    return _hasher.hash(raw)


def verify_password(raw: str, hashed: str | None) -> bool:
    if hashed is None:
        return False  # compte OAuth-only, pas de mot de passe à comparer (ADR-0006)
    try:
        return _hasher.verify(hashed, raw)
    except VerifyMismatchError:
        return False


def create_access_token(*, user_id: uuid.UUID, tenant_id: uuid.UUID, roles: list[str]) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "roles": roles,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_ttl_minutes),
    }
    return jwt.encode(payload, _private_key, algorithm="RS256", headers={"kid": settings.jwt_key_id})


def decode_access_token(token: str) -> dict:
    """Lève jwt.PyJWTError si invalide/expiré — à charge de l'appelant de traduire en 401.
    identity détient déjà la clé publique : pas besoin de passer par packages/security
    (réservé aux *autres* services, voir ADR-0008)."""
    return jwt.decode(token, _public_key, algorithms=["RS256"])


def generate_refresh_token() -> str:
    """Chaîne aléatoire opaque — jamais un JWT (voir SPEC.md)."""
    return secrets.token_urlsafe(48)


def hash_refresh_token(raw: str) -> str:
    """Hash simple (pas Argon2) : c'est un secret déjà à haute entropie, pas un mot de passe humain."""
    return sha256(raw.encode()).hexdigest()
