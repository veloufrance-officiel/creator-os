"""Configuration — variables d'environnement validées (voir .env.example à la racine)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://creator_os:local_dev_only@localhost:5432/creator_os"
    # Base partagée avec identity pour l'instant (ADR-0009) — DATABASE_URL distinct
    # dès qu'une séparation physique sera justifiée, sans rupture de contrat.
    identity_base_url: str = "http://localhost:8000"


settings = Settings()
