"""Authentification — délègue la vérification à packages/security (ADR-0008).
Pas de logique de vérification JWT ici : c'est exactement ce que ce package
partagé évite de réimplémenter par service."""
import uuid
from dataclasses import dataclass

from creator_os_security import InvalidIdentityToken, verify_identity_token
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentTenant:
    user_id: uuid.UUID
    tenant_id: uuid.UUID


async def require_tenant(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentTenant:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Authentification requise.")
    try:
        claims = verify_identity_token(credentials.credentials, identity_base_url=settings.identity_base_url)
    except InvalidIdentityToken as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token invalide ou expiré.") from exc

    return CurrentTenant(user_id=uuid.UUID(claims.user_id), tenant_id=uuid.UUID(claims.tenant_id))
