"""Dépendances FastAPI : authentification (JWT) et vérification de permission (RBAC)."""
import uuid
from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app import repository, security
from app.database import get_db

_bearer = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    id: uuid.UUID
    tenant_id: uuid.UUID
    roles: list[str]


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Authentification requise.")
    try:
        payload = security.decode_access_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token invalide ou expiré.") from exc

    return CurrentUser(
        id=uuid.UUID(payload["sub"]),
        tenant_id=uuid.UUID(payload["tenant_id"]),
        roles=payload.get("roles", []),
    )


def require_permission(code: str):
    """Deny by default (voir SECURITY.md) : la permission doit être explicitement accordée."""

    async def _check(
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> CurrentUser:
        granted = await repository.get_user_permission_codes(db, current_user.id)
        if code not in granted:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail=f"Permission manquante : {code}")
        return current_user

    return _check
