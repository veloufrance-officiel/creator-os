"""Hachage de mot de passe (ADR-0004) et JWT (ADR-0005)."""
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from hashlib import sha256

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.config import settings

_hasher = PasswordHasher()


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
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    """Lève jwt.PyJWTError si invalide/expiré — à charge de l'appelant de traduire en 401."""
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])


def generate_refresh_token() -> str:
    """Chaîne aléatoire opaque — jamais un JWT (voir SPEC.md)."""
    return secrets.token_urlsafe(48)


def hash_refresh_token(raw: str) -> str:
    """Hash simple (pas Argon2) : c'est un secret déjà à haute entropie, pas un mot de passe humain."""
    return sha256(raw.encode()).hexdigest()
