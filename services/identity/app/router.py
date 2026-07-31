"""Routes HTTP — voir SPEC.md. Traduit AuthError en réponses HTTP génériques (pas de fuite d'info)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import repository, schemas, service
from app.database import get_db
from app.oauth import base as oauth_base
from app.oauth.apple import AppleOAuthProvider
from app.oauth.google import GoogleOAuthProvider
from app.oauth.oidc import InvalidIdToken
from app.rbac import CurrentUser, get_current_user, require_permission

router = APIRouter()

# Flow redirection (web) — Google uniquement pour l'instant.
_REDIRECT_PROVIDERS = {"google": GoogleOAuthProvider()}

# Flow ID token natif (mobile + web SDK) — voir ADR-0007. Google réutilise la même
# instance : un provider peut supporter les deux mécanismes à la fois.
_TOKEN_PROVIDERS: dict[str, oauth_base.OAuthProvider] = {
    "google": _REDIRECT_PROVIDERS["google"],
    "apple": AppleOAuthProvider(),
}


def get_oauth_provider(provider: str) -> oauth_base.OAuthProvider:
    """Dépendance surchargeable en test (voir tests/test_oauth_flow.py) — évite tout
    appel réseau réel vers Google pendant les tests (SPEC.md)."""
    instance = _REDIRECT_PROVIDERS.get(provider)
    if instance is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Provider OAuth inconnu : {provider}")
    return instance


def get_token_provider(provider: str) -> oauth_base.OAuthProvider:
    instance = _TOKEN_PROVIDERS.get(provider)
    if instance is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Provider OAuth inconnu : {provider}")
    return instance


@router.post("/auth/register", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: schemas.RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        _, access, refresh = await service.register(db, email=body.email, password=body.password)
    except service.AuthError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return schemas.TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/auth/login", response_model=schemas.TokenResponse)
async def login(body: schemas.LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        _, access, refresh = await service.login(db, email=body.email, password=body.password)
    except service.AuthError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return schemas.TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/auth/refresh", response_model=schemas.TokenResponse)
async def refresh_token(body: schemas.RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        access, refresh = await service.refresh(db, refresh_token=body.refresh_token)
    except service.AuthError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return schemas.TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: schemas.LogoutRequest, db: AsyncSession = Depends(get_db)):
    await service.logout(db, refresh_token=body.refresh_token)


@router.get("/me", response_model=schemas.UserResponse)
async def me(current_user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await repository.get_user_by_id(db, current_user.id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Utilisateur introuvable.")
    return schemas.UserResponse(
        id=user.id, email=user.email, tenant_id=user.tenant_id, roles=current_user.roles, created_at=user.created_at
    )


@router.get("/auth/oauth/{provider}/authorize")
async def oauth_authorize(oauth_provider: oauth_base.OAuthProvider = Depends(get_oauth_provider)):
    state = oauth_base.create_state_token()
    return {"authorization_url": oauth_provider.get_authorization_url(state)}


@router.get("/auth/oauth/{provider}/callback", response_model=schemas.TokenResponse)
async def oauth_callback(
    provider: str,
    code: str,
    state: str,
    oauth_provider: oauth_base.OAuthProvider = Depends(get_oauth_provider),
    db: AsyncSession = Depends(get_db),
):
    try:
        oauth_base.verify_state_token(state)
    except oauth_base.InvalidOAuthState as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    info = await oauth_provider.exchange_code_for_user_info(code)
    try:
        access, refresh = await service.oauth_login_or_register(db, provider=provider, info=info)
    except service.AuthError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return schemas.TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/auth/oauth/{provider}/token", response_model=schemas.TokenResponse)
async def oauth_token_signin(
    provider: str,
    body: schemas.IdTokenRequest,
    oauth_provider: oauth_base.OAuthProvider = Depends(get_token_provider),
    db: AsyncSession = Depends(get_db),
):
    """Sign-in natif (mobile SDK ou JS SDK web) — voir ADR-0007. Pas de state/CSRF
    ici : le token est déjà produit par le SDK du provider sur l'appareil du client,
    ce n'est pas un flow de redirection navigateur."""
    try:
        info = await oauth_provider.verify_id_token(body.id_token)
    except InvalidIdToken as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    try:
        access, refresh = await service.oauth_login_or_register(db, provider=provider, info=info)
    except service.AuthError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return schemas.TokenResponse(access_token=access, refresh_token=refresh)


@router.get("/audit-logs", response_model=list[schemas.AuditLogResponse])
async def audit_logs(
    current_user: CurrentUser = Depends(require_permission("identity:audit_log:read")),
    db: AsyncSession = Depends(get_db),
):
    entries = await repository.list_audit_logs(db, tenant_id=current_user.tenant_id)
    return [
        schemas.AuditLogResponse(
            id=e.id, action=e.action, user_id=e.user_id, event_metadata=e.event_metadata, created_at=e.created_at
        )
        for e in entries
    ]
