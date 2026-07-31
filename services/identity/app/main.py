"""Point d'entrée FastAPI — services/identity. Voir SPEC.md."""
from fastapi import FastAPI

from app import security
from app.router import router

app = FastAPI(
    title="Creator OS — Identity Service",
    version="0.1.0",
    description="Auth, IAM, RBAC, tenants, sessions, audit — Sprint F1/F2.",
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
