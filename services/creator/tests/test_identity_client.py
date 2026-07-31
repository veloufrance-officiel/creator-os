"""Teste app/identity_client.py directement (pas via l'API) avec un faux transport
httpx — vérifie le parsing et la gestion d'erreur réelle, pas seulement la
substitution utilisée dans test_creator_quota.py."""
import httpx
import pytest

from app.identity_client import fetch_account_type


@pytest.mark.parametrize(
    ("handler", "expected"),
    [
        (lambda req: httpx.Response(200, json={"account_type": "team"}), "team"),
        (lambda req: httpx.Response(401, json={"detail": "Token invalide."}), None),
        (lambda req: httpx.Response(500), None),
        (lambda req: httpx.Response(200, json={"unexpected": "shape"}), None),
        (lambda req: httpx.Response(200, content=b"not json"), None),
    ],
)
async def test_fetch_account_type(monkeypatch, handler, expected):
    def _client_init(self, *args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(handler)
        real_init(self, *args, **kwargs)

    real_init = httpx.AsyncClient.__init__
    monkeypatch.setattr(httpx.AsyncClient, "__init__", _client_init)

    result = await fetch_account_type("some-token", identity_base_url="http://identity.internal")
    assert result == expected


async def test_fetch_account_type_forwards_bearer_token():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["authorization"] = request.headers.get("authorization")
        return httpx.Response(200, json={"account_type": "personal"})

    def _client_init(self, *args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(handler)
        real_init(self, *args, **kwargs)

    real_init = httpx.AsyncClient.__init__
    import unittest.mock

    with unittest.mock.patch.object(httpx.AsyncClient, "__init__", _client_init):
        await fetch_account_type("my-raw-token", identity_base_url="http://identity.internal")

    assert seen["authorization"] == "Bearer my-raw-token"
