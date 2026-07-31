"""Tests du quota de créateurs par type de compte (ADR-0012). Le lookup vers
identity est simulé — ces tests vérifient la logique de quota de creator, pas
le comportement réel d'identity (déjà testé côté services/identity)."""
import pytest

from app.main import app
from app.router import get_account_type


def _override_account_type(value):
    async def _fn():
        return value

    return _fn


@pytest.fixture
def as_account_type():
    """Change le type de compte simulé pour la durée d'un test, puis restaure
    le défaut ('enterprise') posé par la fixture `client`."""

    def _set(value):
        app.dependency_overrides[get_account_type] = _override_account_type(value)

    yield _set
    app.dependency_overrides[get_account_type] = _override_account_type("enterprise")


async def test_personal_account_blocked_at_second_creator(client, as_account_type):
    as_account_type("personal")
    first = await client.post("/creators", json={"display_name": "Solo"})
    assert first.status_code == 201

    second = await client.post("/creators", json={"display_name": "Second"})
    assert second.status_code == 409


async def test_team_account_allows_up_to_ten_creators(client, as_account_type):
    as_account_type("team")
    for i in range(10):
        resp = await client.post("/creators", json={"display_name": f"Creator {i}"})
        assert resp.status_code == 201, f"creator {i} devrait passer (quota team = 10)"

    eleventh = await client.post("/creators", json={"display_name": "Eleventh"})
    assert eleventh.status_code == 409


async def test_enterprise_account_has_no_quota(client, as_account_type):
    as_account_type("enterprise")
    for i in range(15):  # au-delà du quota team, doit quand même passer
        resp = await client.post("/creators", json={"display_name": f"Creator {i}"})
        assert resp.status_code == 201

    listing = await client.get("/creators")
    assert len(listing.json()) == 15


async def test_quota_exceeded_message_names_the_account_type(client, as_account_type):
    as_account_type("personal")
    await client.post("/creators", json={"display_name": "First"})
    resp = await client.post("/creators", json={"display_name": "Second"})
    assert "personal" in resp.json()["detail"]


async def test_identity_unreachable_fails_open_creation_not_blocked(client, as_account_type):
    """ADR-0012 : le quota n'est pas une frontière de sécurité — une panne d'identity
    ne doit pas empêcher la création d'un créateur."""
    as_account_type(None)  # simule un identity injoignable (voir identity_client.py)
    for i in range(3):  # dépasserait le quota personal, mais aucun quota connu ici
        resp = await client.post("/creators", json={"display_name": f"Creator {i}"})
        assert resp.status_code == 201
