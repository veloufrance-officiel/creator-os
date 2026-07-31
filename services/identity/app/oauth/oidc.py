"""Vérification générique d'un ID token OIDC — partagée entre providers
(voir ADR-0007). Un provider = un issuer + une JWKS URL + une liste d'audiences
valides ; la logique de vérification de signature est la même pour tous.
"""
import jwt
from jwt import PyJWKClient

from app.oauth.base import OAuthUserInfo

_jwks_clients: dict[str, PyJWKClient] = {}


def _get_jwks_client(jwks_url: str) -> PyJWKClient:
    # Un client par JWKS URL, réutilisé (PyJWKClient met les clés en cache lui-même).
    if jwks_url not in _jwks_clients:
        _jwks_clients[jwks_url] = PyJWKClient(jwks_url)
    return _jwks_clients[jwks_url]


class InvalidIdToken(Exception):
    pass


def verify_oidc_id_token(
    *, id_token: str, issuer: str, audiences: list[str], jwks_url: str
) -> dict:
    if not audiences:
        raise InvalidIdToken("Aucune audience configurée pour ce provider — voir .env.example")

    signing_key = _get_jwks_client(jwks_url).get_signing_key_from_jwt(id_token)
    try:
        claims = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=audiences,
            issuer=issuer,
        )
    except jwt.PyJWTError as exc:
        raise InvalidIdToken(f"ID token invalide : {exc}") from exc
    return claims


def normalize_email_verified(value) -> bool:
    """Apple encode parfois email_verified en chaîne 'true'/'false' plutôt qu'un
    booléen JSON — piège classique (voir ADR-0007) si on fait juste bool(value)."""
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def claims_to_user_info(claims: dict) -> OAuthUserInfo:
    return OAuthUserInfo(
        provider_account_id=claims["sub"],
        email=claims["email"],
        email_verified=normalize_email_verified(claims.get("email_verified", False)),
    )
