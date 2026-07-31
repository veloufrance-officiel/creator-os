"""Fixtures pytest — base SQLite en mémoire (voir database.py::GUID). L'authentification
est simulée par surcharge de dépendance : ces tests vérifient la logique de creator,
pas packages/security (déjà testé séparément dans packages/security/tests/)."""
import uuid

import pytest
import pytest_asyncio
from fastapi import Request
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.auth import CurrentTenant, require_tenant
from app.database import Base, get_db
from app.main import app
from app.router import get_account_type


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def tenant_a():
    return CurrentTenant(user_id=uuid.uuid4(), tenant_id=uuid.uuid4(), raw_token="fake-token-a")


@pytest.fixture
def tenant_b():
    return CurrentTenant(user_id=uuid.uuid4(), tenant_id=uuid.uuid4(), raw_token="fake-token-b")


@pytest_asyncio.fixture
async def client(db_session, tenant_a):
    async def _override_get_db():
        yield db_session

    async def _override_require_tenant():
        return tenant_a

    async def _override_account_type():
        # Défaut généreux : les tests qui ne portent pas spécifiquement sur le quota
        # (ADR-0012) ne doivent pas être bloqués par hasard. Les tests de quota
        # surchargent explicitement cette dépendance avec une valeur précise.
        return "enterprise"

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[require_tenant] = _override_require_tenant
    app.dependency_overrides[get_account_type] = _override_account_type
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client_as(db_session):
    """Comme `client`, mais permet plusieurs clients simultanés authentifiés en tant
    que tenants différents — pour les tests d'isolation entre tenants.

    Piège évité : app.dependency_overrides est un dict global sur l'objet `app`, pas
    par client. Fixer le tenant à la création du client écraserait silencieusement le
    tenant de tout autre client déjà créé. L'identité est donc portée par requête, via
    un header lu par la dépendance surchargée, plutôt que par closure."""

    async def _override_get_db():
        yield db_session

    async def _override_require_tenant(request: Request) -> CurrentTenant:
        return CurrentTenant(
            user_id=uuid.UUID(request.headers["x-test-user-id"]),
            tenant_id=uuid.UUID(request.headers["x-test-tenant-id"]),
            raw_token="fake-token",
        )

    async def _override_account_type():
        return "enterprise"

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[require_tenant] = _override_require_tenant
    app.dependency_overrides[get_account_type] = _override_account_type

    clients: list[AsyncClient] = []

    async def _make(tenant: CurrentTenant) -> AsyncClient:
        transport = ASGITransport(app=app)
        c = AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"x-test-user-id": str(tenant.user_id), "x-test-tenant-id": str(tenant.tenant_id)},
        )
        clients.append(c)
        return c

    yield _make

    for c in clients:
        await c.aclose()
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def unauthenticated_client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
