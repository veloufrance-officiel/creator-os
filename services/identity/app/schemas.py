"""Schémas Pydantic — contrats d'API. Voir SPEC.md pour la liste des routes."""
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class IdTokenRequest(BaseModel):
    """Voir ADR-0007 : jeton obtenu par le client via le SDK natif du provider."""

    id_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    tenant_id: uuid.UUID
    roles: list[str]
    created_at: datetime


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    action: str
    user_id: uuid.UUID | None
    event_metadata: dict
    created_at: datetime


class ErrorResponse(BaseModel):
    detail: str
