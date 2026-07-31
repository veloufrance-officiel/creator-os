"""Implémentation Google du protocole OAuthProvider (app/oauth/base.py)."""
from urllib.parse import urlencode

import httpx

from app.config import settings
from app.oauth.base import OAuthUserInfo

AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"


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

    def _redirect_uri(self) -> str:
        return f"{settings.oauth_redirect_base_url}/auth/oauth/google/callback"
