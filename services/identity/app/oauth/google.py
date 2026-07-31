"""Implémentation Google du protocole OAuthProvider (app/oauth/base.py)."""
from urllib.parse import urlencode

import httpx

from app.config import settings
from app.oauth import oidc
from app.oauth.base import OAuthUserInfo

AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"
JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
# Google a historiquement émis les deux formes en tant qu'issuer valide.
VALID_ISSUERS = ("https://accounts.google.com", "accounts.google.com")


class GoogleOAuthProvider:
    name = "google"

    def get_authorization_url(self, state: str) -> str:
        params = {
            "client_id": settings.google_oauth_client_id,
            "redirect_uri": self._redirect_uri(),
            "response_type": "code",
            "scope": "openid email",
            "state": state,
            "access_type": "online",
        }
        return f"{AUTHORIZATION_ENDPOINT}?{urlencode(params)}"

    async def exchange_code_for_user_info(self, code: str) -> OAuthUserInfo:
        async with httpx.AsyncClient(timeout=10) as client:
            token_resp = await client.post(
                TOKEN_ENDPOINT,
                data={
                    "client_id": settings.google_oauth_client_id,
                    "client_secret": settings.google_oauth_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self._redirect_uri(),
                },
            )
            token_resp.raise_for_status()
            access_token = token_resp.json()["access_token"]

            userinfo_resp = await client.get(
                USERINFO_ENDPOINT, headers={"Authorization": f"Bearer {access_token}"}
            )
            userinfo_resp.raise_for_status()
            data = userinfo_resp.json()

        return OAuthUserInfo(
            provider_account_id=data["sub"],
            email=data["email"],
            email_verified=bool(data.get("email_verified", False)),
        )

    async def verify_id_token(self, id_token: str) -> OAuthUserInfo:
        """Flow natif mobile/web SDK — voir ADR-0007. Complète (ne remplace pas)
        exchange_code_for_user_info, utilisé par le flow redirection existant."""
        last_error: oidc.InvalidIdToken | None = None
        for issuer in VALID_ISSUERS:
            try:
                claims = oidc.verify_oidc_id_token(
                    id_token=id_token,
                    issuer=issuer,
                    audiences=settings.google_oauth_client_ids_list,
                    jwks_url=JWKS_URL,
                )
                return oidc.claims_to_user_info(claims)
            except oidc.InvalidIdToken as exc:
                last_error = exc
        raise last_error  # les deux formes d'issuer ont échoué

    def _redirect_uri(self) -> str:
        return f"{settings.oauth_redirect_base_url}/auth/oauth/google/callback"
