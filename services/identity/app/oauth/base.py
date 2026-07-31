"""Abstraction provider OAuth — voir ADR-0006. Un fournisseur = une classe
qui implémente OAuthProvider ; aucun code métier ne dépend d'un SDK précis."""
import time
from dataclasses import dataclass
from typing import Protocol

import jwt

from app.config import settings

STATE_TTL_SECONDS = 600  # 10 min pour compléter le flow chez le fournisseur


@dataclass(frozen=True)
class OAuthUserInfo:
    provider_account_id: str
    email: str
    email_verified: bool


class OAuthProvider(Protocol):
    name: str

    def get_authorization_url(self, state: str) -> str: ...

    async def exchange_code_for_user_info(self, code: str) -> OAuthUserInfo: ...


class InvalidOAuthState(Exception):
    pass


def create_state_token() -> str:
    """Anti-CSRF, sans stockage serveur (voir SPEC.md) : signé, courte durée de vie."""
    payload = {"purpose": "oauth_state", "iat": int(time.time()), "exp": int(time.time()) + STATE_TTL_SECONDS}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def verify_state_token(token: str) -> None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise InvalidOAuthState("state invalide ou expiré") from exc
    if payload.get("purpose") != "oauth_state":
        raise InvalidOAuthState("state invalide")
