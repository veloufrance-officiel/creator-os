"""Configuration — variables d'environnement validées (voir .env.example à la racine)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://creator_os:local_dev_only@localhost:5432/creator_os"
    jwt_secret: str = "changeme-in-env-never-use-default-in-production"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 7

    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    oauth_redirect_base_url: str = "http://localhost:8000"

    # Listes séparées par virgules : un client ID par plateforme (web, iOS, Android...).
    # Voir ADR-0007. Le premier de la liste Google reste utilisé comme client_id du
    # flow redirection existant (get_authorization_url / exchange_code_for_user_info).
    google_oauth_client_ids: str = ""
    apple_client_ids: str = ""

    @property
    def google_oauth_client_ids_list(self) -> list[str]:
        ids = [c.strip() for c in self.google_oauth_client_ids.split(",") if c.strip()]
        return ids or ([self.google_oauth_client_id] if self.google_oauth_client_id else [])

    @property
    def apple_client_ids_list(self) -> list[str]:
        return [c.strip() for c in self.apple_client_ids.split(",") if c.strip()]


settings = Settings()
