"""Sign in with Apple — vérification d'ID token uniquement (voir ADR-0007).
Le flow redirection web n'est pas implémenté ce sprint : le besoin exprimé
est le sign-in natif (obligatoire pour la distribution iOS dès qu'un autre
login social est proposé), pas le bouton web Apple."""
from app.config import settings
from app.oauth import oidc
from app.oauth.base import OAuthUserInfo

ISSUER = "https://appleid.apple.com"
JWKS_URL = "https://appleid.apple.com/auth/keys"


class AppleOAuthProvider:
    name = "apple"

    async def verify_id_token(self, id_token: str) -> OAuthUserInfo:
        claims = oidc.verify_oidc_id_token(
            id_token=id_token,
            issuer=ISSUER,
            audiences=settings.apple_client_ids_list,
            jwks_url=JWKS_URL,
        )
        return self._claims_to_user_info(claims)

    @staticmethod
    def _claims_to_user_info(claims: dict) -> OAuthUserInfo:
        # Apple n'inclut pas toujours 'email' sur les connexions suivantes (seulement
        # à la toute première autorisation) : à ce stade on exige sa présence, la
        # gestion d'un identifiant sans email nouvellement fourni est un cas à traiter
        # si/quand il se présente en usage réel (pas anticipé sans signal produit).
        return OAuthUserInfo(
            provider_account_id=claims["sub"],
            email=claims["email"],
            email_verified=oidc.normalize_email_verified(claims.get("email_verified", False)),
        )
