"""Routes HTTP — voir SPEC.md et ADR-0010 (API en collection, agences multi-créateurs)."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import repository, schemas, service
from app.auth import CurrentTenant, require_tenant
from app.database import get_db

router = APIRouter()


def _block_to_response(block) -> schemas.BlockResponse:
    return schemas.BlockResponse(id=block.id, type=block.type, position=block.position, config=block.config)


def _portfolio_to_response(portfolio, *, blocks: list | None = None) -> schemas.PortfolioResponse:
    return schemas.PortfolioResponse(
        id=portfolio.id,
        slug=portfolio.slug,
        title=portfolio.title,
        is_published=portfolio.is_published,
        blocks=[_block_to_response(b) for b in (blocks if blocks is not None else portfolio.blocks)],
        updated_at=portfolio.updated_at,
    )


def _creator_to_response(creator) -> schemas.CreatorResponse:
    return schemas.CreatorResponse(
        id=creator.id,
        display_name=creator.display_name,
        niche=creator.niche,
        tone_of_voice=creator.tone_of_voice,
        audience=creator.audience,
        bio=creator.bio,
        is_authorized=creator.is_authorized,
        updated_at=creator.updated_at,
    )


# --- Creators (collection — un tenant peut en avoir plusieurs, ADR-0010) ---


@router.post("/creators", response_model=schemas.CreatorResponse, status_code=status.HTTP_201_CREATED)
async def create_creator(
    body: schemas.CreatorCreateRequest,
    current: CurrentTenant = Depends(require_tenant),
    db: AsyncSession = Depends(get_db),
):
    creator = await service.create_creator(
        db, user_id=current.user_id, tenant_id=current.tenant_id, fields=body.model_dump()
    )
    return _creator_to_response(creator)


@router.get("/creators", response_model=list[schemas.CreatorResponse])
async def list_creators(current: CurrentTenant = Depends(require_tenant), db: AsyncSession = Depends(get_db)):
    creators = await repository.list_creators_by_tenant(db, current.tenant_id)
    return [_creator_to_response(c) for c in creators]


@router.get("/creators/{creator_id}", response_model=schemas.CreatorResponse)
async def get_creator(
    creator_id: uuid.UUID, current: CurrentTenant = Depends(require_tenant), db: AsyncSession = Depends(get_db)
):
    try:
        creator = await service.get_owned_creator(db, creator_id=creator_id, tenant_id=current.tenant_id)
    except service.NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _creator_to_response(creator)


@router.patch("/creators/{creator_id}", response_model=schemas.CreatorResponse)
async def update_creator(
    creator_id: uuid.UUID,
    body: schemas.CreatorUpdateRequest,
    current: CurrentTenant = Depends(require_tenant),
    db: AsyncSession = Depends(get_db),
):
    try:
        creator = await service.update_creator(
            db, creator_id=creator_id, tenant_id=current.tenant_id, fields=body.model_dump()
        )
    except service.NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _creator_to_response(creator)


@router.delete("/creators/{creator_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_creator(
    creator_id: uuid.UUID, current: CurrentTenant = Depends(require_tenant), db: AsyncSession = Depends(get_db)
):
    try:
        await service.delete_creator(db, creator_id=creator_id, tenant_id=current.tenant_id)
    except service.NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# --- Portfolios (scopés à un créateur précis, ADR-0010) ---


@router.post(
    "/creators/{creator_id}/portfolios", response_model=schemas.PortfolioResponse, status_code=status.HTTP_201_CREATED
)
async def create_portfolio(
    creator_id: uuid.UUID,
    body: schemas.PortfolioCreateRequest,
    current: CurrentTenant = Depends(require_tenant),
    db: AsyncSession = Depends(get_db),
):
    try:
        portfolio = await service.create_portfolio(
            db, creator_id=creator_id, tenant_id=current.tenant_id, slug=body.slug, title=body.title
        )
    except service.NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except service.ConflictError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    # Pas d'accès à portfolio.blocks ici : lazy-load ORM incompatible avec ce contexte
    # async (MissingGreenlet) — un portfolio neuf n'a de toute façon jamais de bloc.
    return _portfolio_to_response(portfolio, blocks=[])


@router.get("/creators/{creator_id}/portfolios", response_model=list[schemas.PortfolioSummaryResponse])
async def list_portfolios(
    creator_id: uuid.UUID, current: CurrentTenant = Depends(require_tenant), db: AsyncSession = Depends(get_db)
):
    portfolios = await repository.list_portfolios_by_creator(db, creator_id=creator_id, tenant_id=current.tenant_id)
    return [
        schemas.PortfolioSummaryResponse(id=p.id, slug=p.slug, title=p.title, is_published=p.is_published)
        for p in portfolios
    ]


@router.get("/creators/{creator_id}/portfolios/{portfolio_id}", response_model=schemas.PortfolioResponse)
async def get_portfolio(
    creator_id: uuid.UUID,
    portfolio_id: uuid.UUID,
    current: CurrentTenant = Depends(require_tenant),
    db: AsyncSession = Depends(get_db),
):
    try:
        portfolio = await service.get_owned_portfolio(
            db, portfolio_id=portfolio_id, creator_id=creator_id, tenant_id=current.tenant_id
        )
    except service.NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _portfolio_to_response(portfolio)


@router.patch("/creators/{creator_id}/portfolios/{portfolio_id}", response_model=schemas.PortfolioResponse)
async def update_portfolio(
    creator_id: uuid.UUID,
    portfolio_id: uuid.UUID,
    body: schemas.PortfolioUpdateRequest,
    current: CurrentTenant = Depends(require_tenant),
    db: AsyncSession = Depends(get_db),
):
    try:
        portfolio = await service.update_portfolio(
            db, portfolio_id=portfolio_id, creator_id=creator_id, tenant_id=current.tenant_id, fields=body.model_dump()
        )
    except service.NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except service.ConflictError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _portfolio_to_response(portfolio)


@router.delete("/creators/{creator_id}/portfolios/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    creator_id: uuid.UUID,
    portfolio_id: uuid.UUID,
    current: CurrentTenant = Depends(require_tenant),
    db: AsyncSession = Depends(get_db),
):
    try:
        await service.delete_portfolio(
            db, portfolio_id=portfolio_id, creator_id=creator_id, tenant_id=current.tenant_id
        )
    except service.NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# --- Blocs ---


@router.post(
    "/creators/{creator_id}/portfolios/{portfolio_id}/blocks",
    response_model=schemas.BlockResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_block(
    creator_id: uuid.UUID,
    portfolio_id: uuid.UUID,
    body: schemas.BlockCreateRequest,
    current: CurrentTenant = Depends(require_tenant),
    db: AsyncSession = Depends(get_db),
):
    try:
        block = await service.add_block(
            db,
            portfolio_id=portfolio_id,
            creator_id=creator_id,
            tenant_id=current.tenant_id,
            type=body.type,
            config=body.config,
            position=body.position,
        )
    except service.NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _block_to_response(block)


@router.patch(
    "/creators/{creator_id}/portfolios/{portfolio_id}/blocks/{block_id}", response_model=schemas.BlockResponse
)
async def update_block(
    creator_id: uuid.UUID,
    portfolio_id: uuid.UUID,
    block_id: uuid.UUID,
    body: schemas.BlockUpdateRequest,
    current: CurrentTenant = Depends(require_tenant),
    db: AsyncSession = Depends(get_db),
):
    try:
        block = await service.update_block(
            db,
            portfolio_id=portfolio_id,
            block_id=block_id,
            creator_id=creator_id,
            tenant_id=current.tenant_id,
            fields=body.model_dump(),
        )
    except service.NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _block_to_response(block)


@router.delete(
    "/creators/{creator_id}/portfolios/{portfolio_id}/blocks/{block_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_block(
    creator_id: uuid.UUID,
    portfolio_id: uuid.UUID,
    block_id: uuid.UUID,
    current: CurrentTenant = Depends(require_tenant),
    db: AsyncSession = Depends(get_db),
):
    try:
        await service.delete_block(
            db, portfolio_id=portfolio_id, block_id=block_id, creator_id=creator_id, tenant_id=current.tenant_id
        )
    except service.NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# --- Public ---


@router.get("/public/portfolios/{slug}", response_model=schemas.PublicPortfolioResponse)
async def public_portfolio(slug: str, db: AsyncSession = Depends(get_db)):
    try:
        portfolio = await service.get_public_portfolio(db, slug)
    except service.NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return schemas.PublicPortfolioResponse(
        slug=portfolio.slug, title=portfolio.title, blocks=[_block_to_response(b) for b in portfolio.blocks]
    )
