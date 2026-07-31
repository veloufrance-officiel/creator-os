"""Tests OAuth — provider Google remplacé par un faux (voir SPEC.md : pas d'appel
réseau réel en test). Couvre la politique de rattachement de l'ADR-0006."""
import pytest

from app.main import app
from app.oauth.base import OAuthUserInfo
from app.router import get_oauth_provider


class FakeOAuthProvider:
    name = "google"

    def __init__(self, user_info: OAuthUserInfo):
        self._user_info = user_info

    def get_authorization_url(self, state: str) -> str:
        return f"https://fake-provider.test/authorize?state={state}"

    async def exchange_code_for_user_info(self, code: str) -> OAuthUserInfo:
        return self._user_info


@pytest.fixture
def fake_google(request):
    info = getattr(request, "param", OAuthUserInfo("google-uid-1", "ada@creator-os.dev", True))
    app.dependency_overrides[get_oauth_provider] = lambda: FakeOAuthProvider(info)
    yield info
    app.dependency_overrides.pop(get_oauth_provider, None)


async def _get_state(client) -> str:
    resp = await client.get("/auth/oauth/google/authorize")
    assert resp.status_code == 200
    url = resp.json()["authorization_url"]
    return url.split("state=")[1]


async def test_authorize_returns_a_url_with_state(client, fake_google):
    resp = await client.get("/auth/oauth/google/authorize")
    assert resp.status_code == 200
    assert "state=" in resp.json()["authorization_url"]


async def test_unknown_provider_returns_404(client):
    resp = await client.get("/auth/oauth/github/authorize")
    assert resp.status_code == 404


async def test_callback_creates_new_account_when_no_existing_user(client, fake_google):
    state = await _get_state(client)
    resp = await client.get("/auth/oauth/google/callback", params={"code": "fake-code", "state": state})
    assert resp.status_code == 200
    assert "access_token" in resp.json()

    me = await client.get("/me", headers={"Authorization": f"Bearer {resp.json()['access_token']}"})
    assert me.json()["email"] == fake_google.email


async def test_callback_with_invalid_state_is_rejected(client, fake_google):
    resp = await client.get("/auth/oauth/google/callback", params={"code": "fake-code", "state": "garbage"})
    assert resp.status_code == 400


async def test_callback_second_time_same_account_logs_in_not_duplicate(client, fake_google):
    state1 = await _get_state(client)
    first = await client.get("/auth/oauth/google/callback", params={"code": "c1", "state": state1})
    first_user = (
        await client.get("/me", headers={"Authorization": f"Bearer {first.json()['access_token']}"})
    ).json()

    state2 = await _get_state(client)
    second = await client.get("/auth/oauth/google/callback", params={"code": "c2", "state": state2})
    second_user = (
        await client.get("/me", headers={"Authorization": f"Bearer {second.json()['access_token']}"})
    ).json()

    assert first_user["id"] == second_user["id"]  # même compte, pas de doublon


@pytest.mark.parametrize(
    "fake_google",
    [OAuthUserInfo("google-uid-2", "existing@creator-os.dev", True)],
    indirect=True,
)
async def test_callback_links_to_existing_verified_email_account(client, fake_google, registered_user_payload):
    # Un compte email/mot de passe existe déjà avec le même email que le provider renvoie.
    email = "existing@creator-os.dev"
    register_resp = await client.post(
        "/auth/register", json={"email": email, "password": "correct-horse-battery", "account_type": "personal"}
    )
    original_user_id = (
        await client.get("/me", headers={"Authorization": f"Bearer {register_resp.json()['access_token']}"})
    ).json()["id"]

    state = await _get_state(client)
    oauth_resp = await client.get("/auth/oauth/google/callback", params={"code": "c1", "state": state})
    linked_user_id = (
        await client.get("/me", headers={"Authorization": f"Bearer {oauth_resp.json()['access_token']}"})
    ).json()["id"]

    assert linked_user_id == original_user_id  # rattaché, pas un second compte


@pytest.mark.parametrize(
    "fake_google",
    [OAuthUserInfo("google-uid-3", "unverified@creator-os.dev", False)],
    indirect=True,
)
async def test_callback_rejects_when_existing_email_not_verified_by_provider(client, fake_google):
    email = "unverified@creator-os.dev"
    await client.post(
        "/auth/register", json={"email": email, "password": "correct-horse-battery", "account_type": "personal"}
    )

    state = await _get_state(client)
    oauth_resp = await client.get("/auth/oauth/google/callback", params={"code": "c1", "state": state})

    # Ni doublon de compte (email unique) ni rattachement silencieux : rejet explicite (ADR-0006)
    assert oauth_resp.status_code == 409


async def test_oauth_only_account_cannot_login_with_password(client, fake_google):
    state = await _get_state(client)
    resp = await client.get("/auth/oauth/google/callback", params={"code": "c1", "state": state})
    assert resp.status_code == 200

    login_attempt = await client.post(
        "/auth/login", json={"email": fake_google.email, "password": "whatever-guess"}
    )
    assert login_attempt.status_code == 401
