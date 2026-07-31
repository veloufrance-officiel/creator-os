"""Configuration — variables d'environnement validées (voir .env.example à la racine)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://creator_os:local_dev_only@localhost:5432/creator_os"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 7

    # RS256 (ADR-0008). Vide en dev = paire générée en mémoire au démarrage (non
    # persistante, jamais utiliser cette voie en production — voir SECURITY.md).
    jwt_private_key_pem: str = ""
    jwt_public_key_pem: str = ""
    jwt_key_id: str = "identity-dev-key-1"

    # HS256 volontairement conservé ici : le state OAuth (anti-CSRF) est émis et
    # vérifié par identity uniquement, jamais par un autre service (ADR-0008 ne
    # s'applique qu'aux tokens consommés par d'autres services).
    oauth_state_secret: str = "changeme-in-env-never-use-default-in-production"

    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    oauth_redirect_base_url: str = "http://localhost:8000"

    # Listes séparées par virgules : un client ID par plateforme (web, iOS, Android...).
    # Voir ADR-0007. Le premier de la liste Google reste utilisé comme client_id du
    # flow redirection existant (get_authorization_url / exchange_code_for_user_info).
    google_oauth_client_ids: str = ""
    apple_client_ids: str = ""

    # Origines autorisées pour apps/web (CORS) — voir SECURITY.md. Par défaut, les
    # ports de dev habituels (Next.js). À restreindre au(x) vrai(s) domaine(s) en prod.
    cors_allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]

    @property
    def google_oauth_client_ids_list(self) -> list[str]:
        ids = [c.strip() for c in self.google_oauth_client_ids.split(",") if c.strip()]
        return ids or ([self.google_oauth_client_id] if self.google_oauth_client_id else [])

    @property
    def apple_client_ids_list(self) -> list[str]:
        return [c.strip() for c in self.apple_client_ids.split(",") if c.strip()]


settings = Settings()
