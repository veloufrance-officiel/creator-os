"""Accès base de données — aucune logique métier ici (voir service.py)."""
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models


async def get_user_by_email(db: AsyncSession, email: str) -> models.User | None:
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> models.User | None:
    return await db.get(models.User, user_id)


async def create_tenant(db: AsyncSession, name: str) -> models.Tenant:
    tenant = models.Tenant(name=name)
    db.add(tenant)
    await db.flush()
    return tenant


async def create_user(
    db: AsyncSession, *, tenant_id: uuid.UUID, email: str, hashed_password: str | None
) -> models.User:
    user = models.User(tenant_id=tenant_id, email=email, hashed_password=hashed_password)
    db.add(user)
    await db.flush()
    return user


async def create_role(db: AsyncSession, *, tenant_id: uuid.UUID, name: str) -> models.Role:
    role = models.Role(tenant_id=tenant_id, name=name)
    db.add(role)
    await db.flush()
    return role


async def get_or_create_permission(db: AsyncSession, *, code: str, description: str = "") -> models.Permission:
    result = await db.execute(select(models.Permission).where(models.Permission.code == code))
    permission = result.scalar_one_or_none()
    if permission is None:
        permission = models.Permission(code=code, description=description)
        db.add(permission)
        await db.flush()
    return permission


async def grant_permission_to_role(db: AsyncSession, *, role_id: uuid.UUID, permission_id: uuid.UUID) -> None:
    db.add(models.RolePermission(role_id=role_id, permission_id=permission_id))
    await db.flush()


async def assign_role_to_user(db: AsyncSession, *, user_id: uuid.UUID, role_id: uuid.UUID) -> None:
    db.add(models.UserRole(user_id=user_id, role_id=role_id))
    await db.flush()


async def get_user_role_codes(db: AsyncSession, user_id: uuid.UUID) -> list[str]:
    result = await db.execute(
        select(models.Role.name)
        .join(models.UserRole, models.UserRole.role_id == models.Role.id)
        .where(models.UserRole.user_id == user_id)
    )
    return [row[0] for row in result.all()]


async def get_user_permission_codes(db: AsyncSession, user_id: uuid.UUID) -> set[str]:
    result = await db.execute(
        select(models.Permission.code)
        .join(models.RolePermission, models.RolePermission.permission_id == models.Permission.id)
        .join(models.Role, models.Role.id == models.RolePermission.role_id)
        .join(models.UserRole, models.UserRole.role_id == models.Role.id)
        .where(models.UserRole.user_id == user_id)
    )
    return {row[0] for row in result.all()}


async def create_session(
    db: AsyncSession, *, user_id: uuid.UUID, refresh_token_hash: str, expires_at: datetime
) -> models.Session:
    session = models.Session(user_id=user_id, refresh_token_hash=refresh_token_hash, expires_at=expires_at)
    db.add(session)
    await db.flush()
    return session


async def get_active_session_by_token_hash(db: AsyncSession, token_hash: str) -> models.Session | None:
    result = await db.execute(
        select(models.Session).where(
            models.Session.refresh_token_hash == token_hash,
            models.Session.revoked_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def revoke_session(db: AsyncSession, session: models.Session, *, at: datetime) -> None:
    session.revoked_at = at
    await db.flush()


async def get_oauth_account(db: AsyncSession, *, provider: str, provider_account_id: str) -> models.OAuthAccount | None:
    result = await db.execute(
        select(models.OAuthAccount).where(
            models.OAuthAccount.provider == provider,
            models.OAuthAccount.provider_account_id == provider_account_id,
        )
    )
    return result.scalar_one_or_none()


async def create_oauth_account(
    db: AsyncSession, *, user_id: uuid.UUID, provider: str, provider_account_id: str
) -> models.OAuthAccount:
    account = models.OAuthAccount(user_id=user_id, provider=provider, provider_account_id=provider_account_id)
    db.add(account)
    await db.flush()
    return account


async def write_audit_log(
    db: AsyncSession,
    *,
    action: str,
    tenant_id: uuid.UUID | None,
    user_id: uuid.UUID | None,
    metadata: dict | None = None,
) -> models.AuditLog:
    entry = models.AuditLog(action=action, tenant_id=tenant_id, user_id=user_id, event_metadata=metadata or {})
    db.add(entry)
    await db.flush()
    return entry


async def list_audit_logs(db: AsyncSession, *, tenant_id: uuid.UUID, limit: int = 50) -> list[models.AuditLog]:
    result = await db.execute(
        select(models.AuditLog)
        .where(models.AuditLog.tenant_id == tenant_id)
        .order_by(models.AuditLog.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
