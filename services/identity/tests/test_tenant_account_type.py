"""Tests du type de compte à l'inscription (ADR-0011)."""
import pytest


@pytest.mark.parametrize("account_type", ["personal", "team", "enterprise"])
async def test_register_accepts_each_valid_account_type(client, account_type):
    resp = await client.post(
        "/auth/register",
        json={
            "email": f"{account_type}@creator-os.dev",
            "password": "correct-horse-battery",
            "account_type": account_type,
        },
    )
    assert resp.status_code == 201

    tenant = await client.get("/tenant", headers={"Authorization": f"Bearer {resp.json()['access_token']}"})
    assert tenant.json()["account_type"] == account_type


async def test_register_without_account_type_rejected(client):
    """Le choix est requis avant la fin de l'inscription (ADR-0011), pas une valeur implicite."""
    resp = await client.post(
        "/auth/register", json={"email": "no-type@creator-os.dev", "password": "correct-horse-battery"}
    )
    assert resp.status_code == 422


async def test_register_with_invalid_account_type_rejected(client):
    resp = await client.post(
        "/auth/register",
        json={"email": "bad-type@creator-os.dev", "password": "correct-horse-battery", "account_type": "hobbyist"},
    )
    assert resp.status_code == 422


async def test_tenant_requires_auth(client):
    from httpx import ASGITransport, AsyncClient

    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as anon:
        resp = await anon.get("/tenant")
        assert resp.status_code == 401


async def test_update_account_type_and_audit_logged(client, registered_user_payload):
    register_resp = await client.post("/auth/register", json=registered_user_payload)
    access_token = register_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    update_resp = await client.patch("/tenant", json={"account_type": "team"}, headers=headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["account_type"] == "team"

    audit = await client.get("/audit-logs", headers=headers)
    actions = [entry["action"] for entry in audit.json()]
    assert "tenant.account_type_changed" in actions


async def test_oauth_signup_defaults_to_personal(client, monkeypatch):
    import uuid

    from app.main import app
    from app.oauth.base import OAuthUserInfo
    from app.router import get_oauth_provider

    class FakeGoogle:
        name = "google"

        def get_authorization_url(self, state):
            return f"https://fake.test/authorize?state={state}"

        async def exchange_code_for_user_info(self, code):
            return OAuthUserInfo(f"oauth-uid-{uuid.uuid4()}", "oauth-signup@creator-os.dev", True)

    app.dependency_overrides[get_oauth_provider] = lambda: FakeGoogle()
    try:
        from app.oauth.base import create_state_token

        state = create_state_token()
        resp = await client.get("/auth/oauth/google/callback", params={"code": "c1", "state": state})
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}
        tenant = await client.get("/tenant", headers=headers)
        assert tenant.json()["account_type"] == "personal"
    finally:
        app.dependency_overrides.pop(get_oauth_provider, None)
