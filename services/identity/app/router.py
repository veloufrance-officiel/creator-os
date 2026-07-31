"""Routes HTTP — voir SPEC.md. Traduit AuthError en réponses HTTP génériques (pas de fuite d'info)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import repository, schemas, service
from app.database import get_db
from app.rbac import CurrentUser, get_current_user, require_permission

router = APIRouter()


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
