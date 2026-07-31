"""Appel à services/identity pour connaître le type de compte courant — voir
ADR-0012. Transmet le token porteur de l'appelant, pas de nouveau mécanisme
d'auth service-à-service. Fail-open : renvoie None si identity est injoignable,
à charge de l'appelant de décider quoi faire (voir service.py)."""
import httpx


async def fetch_account_type(bearer_token: str, *, identity_base_url: str) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                f"{identity_base_url.rstrip('/')}/tenant",
                headers={"Authorization": f"Bearer {bearer_token}"},
            )
            resp.raise_for_status()
            return resp.json()["account_type"]
    except (httpx.HTTPError, KeyError, ValueError):
        return None
