"""Point d'entrée FastAPI — services/creator. Voir SPEC.md."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.router import router

app = FastAPI(
    title="Creator OS — Creator Service",
    version="0.1.0",
    description="Creator Twin, portfolios — Sprint F2.",
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
    return {"status": "ok", "service": "creator"}
