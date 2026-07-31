"""Logique métier — orchestre repository.py + security.py. Voir SPEC.md pour les flux."""
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app import repository, security
from app.config import settings
from app.oauth.base import OAuthUserInfo

# Catalogue de permissions F1 — voir SPEC.md. Un nouveau service ajoutera les siennes,
# jamais au nom d'identity.
F1_OWNER_PERMISSIONS = ["identity:audit_log:read"]


class AuthError(Exception):
    """Erreur d'authentification — toujours traduite en message générique côté API."""


async def register(db: AsyncSession, *, email: str, password: str) -> tuple[dict, str, str]:
    existing = await repository.get_user_by_email(db, email)
    if existing is not None:
        raise AuthError("Un compte existe déjà avec cet email.")

    user, tenant = await _create_new_account(db, email=email, hashed_password=security.hash_password(password))
    await repository.write_audit_log(
        db, action="user.register", tenant_id=tenant.id, user_id=user.id, metadata={"email": email}
    )

    access, refresh = await _issue_tokens(db, user_id=user.id, tenant_id=tenant.id, roles=["owner"])
    await db.commit()
    return _user_payload(user, ["owner"]), access, refresh


async def oauth_login_or_register(db: AsyncSession, *, provider: str, info: OAuthUserInfo) -> tuple[str, str]:
    """Politique de rattachement de compte — voir ADR-0006."""
    link = await repository.get_oauth_account(db, provider=provider, provider_account_id=info.provider_account_id)
    if link is not None:
        user = await repository.get_user_by_id(db, link.user_id)
        action = "user.login"
    else:
        existing = await repository.get_user_by_email(db, info.email)
        if existing is not None and info.email_verified:
            user = existing
            await repository.create_oauth_account(
                db, user_id=user.id, provider=provider, provider_account_id=info.provider_account_id
            )
            action = "user.oauth_linked"
        elif existing is not None:
            # Email déjà pris mais pas certifié vérifié par le provider : impossible de
            # créer un second compte (email unique) et interdit de rattacher (ADR-0006).
            # Rejet explicite plutôt qu'un conflit de contrainte SQL silencieux.
            raise AuthError(
                "Un compte existe déjà avec cet email. Connectez-vous avec votre mot de passe, "
                "ou vérifiez votre email chez le fournisseur avant de réessayer."
            )
        else:
            user, tenant = await _create_new_account(db, email=info.email, hashed_password=None)
            await repository.create_oauth_account(
                db, user_id=user.id, provider=provider, provider_account_id=info.provider_account_id
            )
            action = "user.oauth_register"

    roles = await repository.get_user_role_codes(db, user.id)
    access, refresh = await _issue_tokens(db, user_id=user.id, tenant_id=user.tenant_id, roles=roles)
    await repository.write_audit_log(
        db, action=action, tenant_id=user.tenant_id, user_id=user.id, metadata={"provider": provider}
    )
    await db.commit()
    return access, refresh


async def _create_new_account(db: AsyncSession, *, email: str, hashed_password: str | None):
    tenant = await repository.create_tenant(db, name=f"Workspace de {email}")
    user = await repository.create_user(db, tenant_id=tenant.id, email=email, hashed_password=hashed_password)
    owner_role = await repository.create_role(db, tenant_id=tenant.id, name="owner")
    for code in F1_OWNER_PERMISSIONS:
        permission = await repository.get_or_create_permission(db, code=code)
        await repository.grant_permission_to_role(db, role_id=owner_role.id, permission_id=permission.id)
    await repository.assign_role_to_user(db, user_id=user.id, role_id=owner_role.id)
    return user, tenant


async def login(db: AsyncSession, *, email: str, password: str) -> tuple[dict, str, str]:
    user = await repository.get_user_by_email(db, email)
    if user is None or not security.verify_password(password, user.hashed_password):
        await repository.write_audit_log(
            db, action="user.login_failed", tenant_id=None, user_id=None, metadata={"email": email}
        )
        await db.commit()
        raise AuthError("Email ou mot de passe incorrect.")

    roles = await repository.get_user_role_codes(db, user.id)
    access, refresh = await _issue_tokens(db, user_id=user.id, tenant_id=user.tenant_id, roles=roles)
    await repository.write_audit_log(db, action="user.login", tenant_id=user.tenant_id, user_id=user.id)
    await db.commit()
    return _user_payload(user, roles), access, refresh


async def refresh(db: AsyncSession, *, refresh_token: str) -> tuple[str, str]:
    token_hash = security.hash_refresh_token(refresh_token)
    session = await repository.get_active_session_by_token_hash(db, token_hash)
    if session is None or _as_utc(session.expires_at) < datetime.now(UTC):
        raise AuthError("Session invalide ou expirée.")

    user = await repository.get_user_by_id(db, session.user_id)
    if user is None:
        raise AuthError("Session invalide ou expirée.")

    await repository.revoke_session(db, session, at=datetime.now(UTC))
    roles = await repository.get_user_role_codes(db, user.id)
    access, new_refresh = await _issue_tokens(db, user_id=user.id, tenant_id=user.tenant_id, roles=roles)
    await db.commit()
    return access, new_refresh


async def logout(db: AsyncSession, *, refresh_token: str) -> None:
    token_hash = security.hash_refresh_token(refresh_token)
    session = await repository.get_active_session_by_token_hash(db, token_hash)
    if session is not None:
        await repository.revoke_session(db, session, at=datetime.now(UTC))
        await repository.write_audit_log(db, action="user.logout", tenant_id=None, user_id=session.user_id)
        await db.commit()


async def _issue_tokens(db: AsyncSession, *, user_id, tenant_id, roles: list[str]) -> tuple[str, str]:
    access = security.create_access_token(user_id=user_id, tenant_id=tenant_id, roles=roles)
    raw_refresh = security.generate_refresh_token()
    expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_ttl_days)
    await repository.create_session(
        db, user_id=user_id, refresh_token_hash=security.hash_refresh_token(raw_refresh), expires_at=expires_at
    )
    return access, raw_refresh


def _as_utc(value: datetime) -> datetime:
    """Postgres (prod) renvoie un datetime tz-aware ; SQLite (tests) le renvoie naïf
    (SQLite n'a pas de type timestamptz natif). On normalise plutôt que de faire
    confiance à un driver pour préserver un tzinfo qu'il ne peut pas stocker."""
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


def _user_payload(user, roles: list[str]) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "tenant_id": user.tenant_id,
        "roles": roles,
        "created_at": user.created_at,
    }
