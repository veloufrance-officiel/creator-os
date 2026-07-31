"""Configuration — variables d'environnement validées (voir .env.example à la racine)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://creator_os:local_dev_only@localhost:5432/creator_os"
    # Base partagée avec identity pour l'instant (ADR-0009) — DATABASE_URL distinct
    # dès qu'une séparation physique sera justifiée, sans rupture de contrat.
    identity_base_url: str = "http://localhost:8000"

    # Origines autorisées pour apps/web (CORS) — mêmes valeurs que identity par défaut.
    cors_allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]


settings = Settings()
