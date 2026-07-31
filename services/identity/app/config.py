"""Configuration — variables d'environnement validées (voir .env.example à la racine)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://creator_os:local_dev_only@localhost:5432/creator_os"
    jwt_secret: str = "changeme-in-env-never-use-default-in-production"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 7


settings = Settings()
