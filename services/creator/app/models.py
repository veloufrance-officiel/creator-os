"""Modèles SQLAlchemy — voir SPEC.md et ADR-0009 (pas de FK vers les tables identity)."""
import uuid
from datetime import datetime, UTC

from sqlalchemy import JSON, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import GUID, Base


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


def _now() -> datetime:
    return datetime.now(UTC)


class Creator(Base):
    """Un par tenant. 'Creator Twin' = ce profil enrichi (ADR-0009), pas une table à part."""

    __tablename__ = "creators"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=_uuid)
    # Pas de ForeignKey : identity et creator sont des services distincts (ADR-0009).
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), unique=True, index=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(GUID(), unique=True, index=True)

    display_name: Mapped[str] = mapped_column(String(200), default="")
    niche: Mapped[str] = mapped_column(String(200), default="")
    tone_of_voice: Mapped[str] = mapped_column(String(500), default="")
    audience: Mapped[str] = mapped_column(String(500), default="")
    bio: Mapped[str] = mapped_column(Text, default="")

    created_at: Mapped[datetime] = mapped_column(default=_now)
    updated_at: Mapped[datetime] = mapped_column(default=_now, onupdate=_now)


class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(GUID(), index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200), default="")
    # Privacy By Default (ADR-0003) : jamais publié à la création.
    is_published: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=_now)
    updated_at: Mapped[datetime] = mapped_column(default=_now, onupdate=_now)

    blocks: Mapped[list["PortfolioBlock"]] = relationship(
        back_populates="portfolio", order_by="PortfolioBlock.position", cascade="all, delete-orphan"
    )


class PortfolioBlock(Base):
    __tablename__ = "portfolio_blocks"
    __table_args__ = (UniqueConstraint("portfolio_id", "position", name="uq_block_portfolio_position"),)

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=_uuid)
    portfolio_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("portfolios.id"), index=True)
    type: Mapped[str] = mapped_column(String(50))  # bio | media_gallery | links | contact (SPEC.md)
    position: Mapped[int] = mapped_column()
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=_now)
    updated_at: Mapped[datetime] = mapped_column(default=_now, onupdate=_now)

    portfolio: Mapped["Portfolio"] = relationship(back_populates="blocks")
