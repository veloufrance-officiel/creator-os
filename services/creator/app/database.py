"""Moteur et session SQLAlchemy async. GUID dupliqué depuis services/identity à
l'identique (voir ADR-0009) : chaque service reste indépendant, pas de package
partagé pour un utilitaire aussi petit — packages/security est réservé à la
vérification de token, un besoin réellement transverse."""
import uuid
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import CHAR, TypeDecorator

from app.config import settings


class Base(DeclarativeBase):
    pass


class GUID(TypeDecorator):
    """UUID portable Postgres (natif) / SQLite (CHAR(36)) — pour que les tests
    tournent sans Postgres réel tout en gardant le même modèle en production."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import UUID as PG_UUID

            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None or dialect.name == "postgresql":
            return value
        return uuid.UUID(value)


engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
