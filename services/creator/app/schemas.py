"""Schémas Pydantic — voir SPEC.md pour la liste des routes."""
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

BlockType = Literal["bio", "media_gallery", "links", "contact"]


class CreatorUpsertRequest(BaseModel):
    display_name: str = Field(default="", max_length=200)
    niche: str = Field(default="", max_length=200)
    tone_of_voice: str = Field(default="", max_length=500)
    audience: str = Field(default="", max_length=500)
    bio: str = Field(default="", max_length=5000)


class CreatorResponse(BaseModel):
    id: uuid.UUID
    display_name: str
    niche: str
    tone_of_voice: str
    audience: str
    bio: str
    updated_at: datetime


class PortfolioCreateRequest(BaseModel):
    slug: str = Field(min_length=3, max_length=100, pattern=r"^[a-z0-9-]+$")
    title: str = Field(default="", max_length=200)


class PortfolioUpdateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    slug: str | None = Field(default=None, min_length=3, max_length=100, pattern=r"^[a-z0-9-]+$")
    is_published: bool | None = None


class BlockCreateRequest(BaseModel):
    type: BlockType
    config: dict = Field(default_factory=dict)
    position: int | None = None  # défaut : ajouté à la fin (voir service.py)


class BlockUpdateRequest(BaseModel):
    config: dict | None = None
    position: int | None = None


class BlockResponse(BaseModel):
    id: uuid.UUID
    type: str
    position: int
    config: dict


class PortfolioResponse(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    is_published: bool
    blocks: list[BlockResponse]
    updated_at: datetime


class PortfolioSummaryResponse(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    is_published: bool


class PublicPortfolioResponse(BaseModel):
    """Volontairement distinct de PortfolioResponse : ne jamais exposer id/tenant_id
    interne sur la route publique, même par accident futur si les deux divergent."""

    slug: str
    title: str
    blocks: list[BlockResponse]
