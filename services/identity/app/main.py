"""Point d'entrée FastAPI — services/identity. Voir SPEC.md."""
from fastapi import FastAPI

from app.router import router

app = FastAPI(
    title="Creator OS — Identity Service",
    version="0.1.0",
    description="Auth, IAM, RBAC, tenants, sessions, audit — Sprint F1.",
)
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "identity"}
