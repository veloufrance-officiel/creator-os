"""Logique métier — orchestre repository.py. Voir SPEC.md pour les règles."""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app import repository


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


async def upsert_creator(db: AsyncSession, *, user_id: uuid.UUID, tenant_id: uuid.UUID, fields: dict):
    creator = await repository.upsert_creator(db, user_id=user_id, tenant_id=tenant_id, fields=fields)
    await db.commit()
    return creator


async def create_portfolio(db: AsyncSession, *, tenant_id: uuid.UUID, slug: str, title: str):
    existing = await repository.get_portfolio_by_slug(db, slug)
    if existing is not None:
        raise ConflictError("Ce slug est déjà utilisé.")
    portfolio = await repository.create_portfolio(db, tenant_id=tenant_id, slug=slug, title=title)
    await db.commit()
    return portfolio


async def get_owned_portfolio(db: AsyncSession, *, portfolio_id: uuid.UUID, tenant_id: uuid.UUID):
    portfolio = await repository.get_portfolio_by_id_and_tenant(db, portfolio_id=portfolio_id, tenant_id=tenant_id)
    if portfolio is None:
        raise NotFoundError("Portfolio introuvable.")
    return portfolio


async def update_portfolio(db: AsyncSession, *, portfolio_id: uuid.UUID, tenant_id: uuid.UUID, fields: dict):
    portfolio = await get_owned_portfolio(db, portfolio_id=portfolio_id, tenant_id=tenant_id)
    new_slug = fields.get("slug")
    if new_slug is not None and new_slug != portfolio.slug:
        existing = await repository.get_portfolio_by_slug(db, new_slug)
        if existing is not None:
            raise ConflictError("Ce slug est déjà utilisé.")
    for key, value in fields.items():
        if value is not None:
            setattr(portfolio, key, value)
    await db.commit()
    return portfolio


async def delete_portfolio(db: AsyncSession, *, portfolio_id: uuid.UUID, tenant_id: uuid.UUID) -> None:
    portfolio = await get_owned_portfolio(db, portfolio_id=portfolio_id, tenant_id=tenant_id)
    await repository.delete_portfolio(db, portfolio)
    await db.commit()


async def get_public_portfolio(db: AsyncSession, slug: str):
    portfolio = await repository.get_portfolio_by_slug(db, slug)
    # Même erreur, publié-mais-inexistant ou existant-mais-privé : ne jamais
    # distinguer les deux cas côté réponse (SPEC.md — pas de fuite d'information).
    if portfolio is None or not portfolio.is_published:
        raise NotFoundError("Portfolio introuvable.")
    return portfolio


async def add_block(
    db: AsyncSession,
    *,
    portfolio_id: uuid.UUID,
    tenant_id: uuid.UUID,
    type: str,
    config: dict,
    position: int | None,
):
    portfolio = await get_owned_portfolio(db, portfolio_id=portfolio_id, tenant_id=tenant_id)
    if position is None:
        position = await repository.get_next_block_position(db, portfolio.id)
    block = await repository.create_block(db, portfolio_id=portfolio.id, type=type, config=config, position=position)
    await db.commit()
    return block


async def update_block(
    db: AsyncSession, *, portfolio_id: uuid.UUID, block_id: uuid.UUID, tenant_id: uuid.UUID, fields: dict
):
    await get_owned_portfolio(db, portfolio_id=portfolio_id, tenant_id=tenant_id)  # vérifie l'appartenance
    block = await repository.get_block(db, block_id=block_id, portfolio_id=portfolio_id)
    if block is None:
        raise NotFoundError("Bloc introuvable.")
    for key, value in fields.items():
        if value is not None:
            setattr(block, key, value)
    await db.commit()
    return block


async def delete_block(db: AsyncSession, *, portfolio_id: uuid.UUID, block_id: uuid.UUID, tenant_id: uuid.UUID) -> None:
    await get_owned_portfolio(db, portfolio_id=portfolio_id, tenant_id=tenant_id)
    block = await repository.get_block(db, block_id=block_id, portfolio_id=portfolio_id)
    if block is None:
        raise NotFoundError("Bloc introuvable.")
    await repository.delete_block(db, block)
    await db.commit()
