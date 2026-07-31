"""Vérification des tokens émis par services/identity — voir ADR-0008.

Tout service qui doit authentifier un appel via un token identity utilise ce
module plutôt que de réimplémenter sa propre vérification JWKS. Ne détient
jamais la clé privée : uniquement la clé publique, récupérée et mise en cache
depuis la JWKS exposée par identity.
"""
from dataclasses import dataclass

import jwt
from jwt import PyJWKClient

_jwks_clients: dict[str, PyJWKClient] = {}


@dataclass(frozen=True)
class IdentityClaims:
    user_id: str
    tenant_id: str
    roles: list[str]


class InvalidIdentityToken(Exception):
    pass


def _get_jwks_client(identity_base_url: str) -> PyJWKClient:
    jwks_url = f"{identity_base_url.rstrip('/')}/.well-known/jwks.json"
    if jwks_url not in _jwks_clients:
        _jwks_clients[jwks_url] = PyJWKClient(jwks_url)
    return _jwks_clients[jwks_url]


def verify_identity_token(token: str, *, identity_base_url: str) -> IdentityClaims:
    """Lève InvalidIdentityToken si signature, expiration, ou forme du token invalide.
    À charge de l'appelant (ex. dépendance FastAPI d'un service) de traduire en 401."""
    try:
        signing_key = _get_jwks_client(identity_base_url).get_signing_key_from_jwt(token)
        claims = jwt.decode(token, signing_key.key, algorithms=["RS256"])
    except jwt.PyJWTError as exc:
        raise InvalidIdentityToken(str(exc)) from exc

    try:
        return IdentityClaims(
            user_id=claims["sub"],
            tenant_id=claims["tenant_id"],
            roles=claims.get("roles", []),
        )
    except KeyError as exc:
        raise InvalidIdentityToken(f"Claim manquante dans le token : {exc}") from exc
