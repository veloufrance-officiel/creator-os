"""Point d'entrée FastAPI — services/identity. Voir SPEC.md."""
from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import security
from app.config import settings
from app.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Migrations au démarrage du process applicatif lui-même -- voir commit :
    le pre-deploy command en process séparé avait un environnement où la
    résolution du package alembic échouait de façon incohérente (4 méthodes
    d'invocation différentes, 4 échecs différents), alors que ce process
    (celui d'uvicorn) importe déjà tout le reste (fastapi, sqlalchemy...)
    sans problème -- migrations rattachées à ce même environnement, connu
    pour fonctionner."""
    cfg = Config("migrations.cfg")
    command.upgrade(cfg, "head")
    yield


app = FastAPI(
    title="Creator OS — Identity Service",
    version="0.1.0",
    description="Auth, IAM, RBAC, tenants, sessions, audit — Sprint F1/F2.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "identity"}


@app.get("/.well-known/jwks.json")
async def jwks():
    """Public, sans auth — voir ADR-0008. Consommé par packages/security depuis les
    autres services pour vérifier les tokens émis ici, sans jamais voir la clé privée."""
    return security.get_jwks()
