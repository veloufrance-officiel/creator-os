"""Point d'entrée FastAPI — services/creator. Voir SPEC.md."""
from fastapi import FastAPI

from app.router import router

app = FastAPI(
    title="Creator OS — Creator Service",
    version="0.1.0",
    description="Creator Twin, portfolios — Sprint F2.",
)
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "creator"}
