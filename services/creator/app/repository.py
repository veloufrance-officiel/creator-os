"""Accès base de données — aucune logique métier ici (voir service.py)."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import models


async def get_creator_by_tenant(db: AsyncSession, tenant_id: uuid.UUID) -> models.Creator | None:
    result = await db.execute(select(models.Creator).where(models.Creator.tenant_id == tenant_id))
    return result.scalar_one_or_none()


async def upsert_creator(db: AsyncSession, *, user_id: uuid.UUID, tenant_id: uuid.UUID, fields: dict) -> models.Creator:
    creator = await get_creator_by_tenant(db, tenant_id)
    if creator is None:
        creator = models.Creator(user_id=user_id, tenant_id=tenant_id, **fields)
        db.add(creator)
    else:
        for key, value in fields.items():
            setattr(creator, key, value)
    await db.flush()
    return creator


async def get_portfolio_by_slug(db: AsyncSession, slug: str) -> models.Portfolio | None:
    result = await db.execute(
        select(models.Portfolio).options(selectinload(models.Portfolio.blocks)).where(models.Portfolio.slug == slug)
    )
    return result.scalar_one_or_none()


async def get_portfolio_by_id_and_tenant(
    db: AsyncSession, *, portfolio_id: uuid.UUID, tenant_id: uuid.UUID
) -> models.Portfolio | None:
    result = await db.execute(
        select(models.Portfolio)
        .options(selectinload(models.Portfolio.blocks))
        .where(models.Portfolio.id == portfolio_id, models.Portfolio.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def list_portfolios_by_tenant(db: AsyncSession, tenant_id: uuid.UUID) -> list[models.Portfolio]:
    result = await db.execute(select(models.Portfolio).where(models.Portfolio.tenant_id == tenant_id))
    return list(result.scalars().all())


async def create_portfolio(db: AsyncSession, *, tenant_id: uuid.UUID, slug: str, title: str) -> models.Portfolio:
    portfolio = models.Portfolio(tenant_id=tenant_id, slug=slug, title=title)
    db.add(portfolio)
    await db.flush()
    return portfolio


async def delete_portfolio(db: AsyncSession, portfolio: models.Portfolio) -> None:
    await db.delete(portfolio)
    await db.flush()


async def get_next_block_position(db: AsyncSession, portfolio_id: uuid.UUID) -> int:
    result = await db.execute(
        select(models.PortfolioBlock.position)
        .where(models.PortfolioBlock.portfolio_id == portfolio_id)
        .order_by(models.PortfolioBlock.position.desc())
        .limit(1)
    )
    last = result.scalar_one_or_none()
    return 0 if last is None else last + 1


async def create_block(
    db: AsyncSession, *, portfolio_id: uuid.UUID, type: str, config: dict, position: int
) -> models.PortfolioBlock:
    block = models.PortfolioBlock(portfolio_id=portfolio_id, type=type, config=config, position=position)
    db.add(block)
    await db.flush()
    return block


async def get_block(db: AsyncSession, *, block_id: uuid.UUID, portfolio_id: uuid.UUID) -> models.PortfolioBlock | None:
    result = await db.execute(
        select(models.PortfolioBlock).where(
            models.PortfolioBlock.id == block_id, models.PortfolioBlock.portfolio_id == portfolio_id
        )
    )
    return result.scalar_one_or_none()


async def delete_block(db: AsyncSession, block: models.PortfolioBlock) -> None:
    await db.delete(block)
    await db.flush()
