"""Tests bout-en-bout via l'API — voir SPEC.md et ADR-0010 (agences multi-créateurs)."""


async def test_create_creator(client):
    resp = await client.post("/creators", json={"display_name": "Ada", "niche": "tech"})
    assert resp.status_code == 201
    assert resp.json()["display_name"] == "Ada"
    assert resp.json()["is_authorized"] is True  # actif par défaut à la création (ADR-0010)


async def test_tenant_can_have_several_creators(client):
    """Cas agence (ADR-0010) : un même tenant gère plusieurs créateurs."""
    a = await client.post("/creators", json={"display_name": "Créateur A"})
    b = await client.post("/creators", json={"display_name": "Créateur B"})
    assert a.json()["id"] != b.json()["id"]

    listing = await client.get("/creators")
    names = {c["display_name"] for c in listing.json()}
    assert names == {"Créateur A", "Créateur B"}


async def test_update_creator(client):
    create_resp = await client.post("/creators", json={"display_name": "Ada"})
    creator_id = create_resp.json()["id"]

    update_resp = await client.patch(f"/creators/{creator_id}", json={"display_name": "Ada L."})
    assert update_resp.json()["display_name"] == "Ada L."
    assert update_resp.json()["id"] == creator_id


async def test_deauthorize_creator(client):
    create_resp = await client.post("/creators", json={"display_name": "Ada"})
    creator_id = create_resp.json()["id"]

    resp = await client.patch(f"/creators/{creator_id}", json={"is_authorized": False})
    assert resp.json()["is_authorized"] is False

    # L'agence garde l'accès interne à un créateur désautorisé (ADR-0010)
    still_readable = await client.get(f"/creators/{creator_id}")
    assert still_readable.status_code == 200


async def test_get_unknown_creator_404(client):
    resp = await client.get("/creators/11111111-1111-1111-1111-111111111111")
    assert resp.status_code == 404


async def test_creators_requires_auth(unauthenticated_client):
    resp = await unauthenticated_client.get("/creators")
    assert resp.status_code == 401


async def test_portfolio_not_published_by_default(client):
    creator = await client.post("/creators", json={"display_name": "Ada"})
    creator_id = creator.json()["id"]

    resp = await client.post(f"/creators/{creator_id}/portfolios", json={"slug": "ada-portfolio", "title": "Ada"})
    assert resp.status_code == 201
    assert resp.json()["is_published"] is False  # Privacy By Default, ADR-0003


async def test_portfolio_for_unknown_creator_404(client):
    resp = await client.post(
        "/creators/11111111-1111-1111-1111-111111111111/portfolios", json={"slug": "orphan"}
    )
    assert resp.status_code == 404


async def test_duplicate_slug_conflicts(client):
    creator = await client.post("/creators", json={"display_name": "Ada"})
    creator_id = creator.json()["id"]
    await client.post(f"/creators/{creator_id}/portfolios", json={"slug": "taken-slug"})
    resp = await client.post(f"/creators/{creator_id}/portfolios", json={"slug": "taken-slug"})
    assert resp.status_code == 409


async def test_public_portfolio_404_when_not_published(client):
    creator = await client.post("/creators", json={"display_name": "Ada"})
    creator_id = creator.json()["id"]
    await client.post(f"/creators/{creator_id}/portfolios", json={"slug": "private-one"})

    resp = await client.get("/public/portfolios/private-one")
    assert resp.status_code == 404


async def test_public_portfolio_404_when_slug_does_not_exist(client):
    resp = await client.get("/public/portfolios/does-not-exist")
    assert resp.status_code == 404


async def test_publishing_makes_portfolio_publicly_visible(client):
    creator = await client.post("/creators", json={"display_name": "Ada"})
    creator_id = creator.json()["id"]
    create_resp = await client.post(
        f"/creators/{creator_id}/portfolios", json={"slug": "now-public", "title": "Public Me"}
    )
    portfolio_id = create_resp.json()["id"]

    await client.patch(f"/creators/{creator_id}/portfolios/{portfolio_id}", json={"is_published": True})

    resp = await client.get("/public/portfolios/now-public")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Public Me"


async def test_deauthorizing_creator_hides_published_portfolio(client):
    """Coeur d'ADR-0010 : désautoriser un créateur le retire du public, même publié."""
    creator = await client.post("/creators", json={"display_name": "Ada"})
    creator_id = creator.json()["id"]
    portfolio = await client.post(f"/creators/{creator_id}/portfolios", json={"slug": "was-public"})
    portfolio_id = portfolio.json()["id"]
    await client.patch(f"/creators/{creator_id}/portfolios/{portfolio_id}", json={"is_published": True})
    assert (await client.get("/public/portfolios/was-public")).status_code == 200

    await client.patch(f"/creators/{creator_id}", json={"is_authorized": False})

    resp = await client.get("/public/portfolios/was-public")
    assert resp.status_code == 404

    # Réautoriser rend le portfolio à nouveau visible, sans rien reconfigurer d'autre
    await client.patch(f"/creators/{creator_id}", json={"is_authorized": True})
    assert (await client.get("/public/portfolios/was-public")).status_code == 200


async def test_blocks_created_updated_deleted(client):
    creator = await client.post("/creators", json={"display_name": "Ada"})
    creator_id = creator.json()["id"]
    create_resp = await client.post(f"/creators/{creator_id}/portfolios", json={"slug": "block-test"})
    portfolio_id = create_resp.json()["id"]

    add_resp = await client.post(
        f"/creators/{creator_id}/portfolios/{portfolio_id}/blocks", json={"type": "bio", "config": {"text": "hello"}}
    )
    assert add_resp.status_code == 201
    block_id = add_resp.json()["id"]
    assert add_resp.json()["position"] == 0

    update_resp = await client.patch(
        f"/creators/{creator_id}/portfolios/{portfolio_id}/blocks/{block_id}", json={"config": {"text": "updated"}}
    )
    assert update_resp.json()["config"]["text"] == "updated"

    delete_resp = await client.delete(f"/creators/{creator_id}/portfolios/{portfolio_id}/blocks/{block_id}")
    assert delete_resp.status_code == 204

    portfolio_resp = await client.get(f"/creators/{creator_id}/portfolios/{portfolio_id}")
    assert portfolio_resp.json()["blocks"] == []


async def test_blocks_auto_increment_position(client):
    creator = await client.post("/creators", json={"display_name": "Ada"})
    creator_id = creator.json()["id"]
    create_resp = await client.post(f"/creators/{creator_id}/portfolios", json={"slug": "position-test"})
    portfolio_id = create_resp.json()["id"]

    first = await client.post(
        f"/creators/{creator_id}/portfolios/{portfolio_id}/blocks", json={"type": "bio", "config": {}}
    )
    second = await client.post(
        f"/creators/{creator_id}/portfolios/{portfolio_id}/blocks", json={"type": "links", "config": {}}
    )

    assert first.json()["position"] == 0
    assert second.json()["position"] == 1


async def test_reorder_block_via_explicit_position(client):
    creator = await client.post("/creators", json={"display_name": "Ada"})
    creator_id = creator.json()["id"]
    create_resp = await client.post(f"/creators/{creator_id}/portfolios", json={"slug": "reorder-test"})
    portfolio_id = create_resp.json()["id"]
    block = await client.post(
        f"/creators/{creator_id}/portfolios/{portfolio_id}/blocks", json={"type": "bio", "config": {}}
    )

    resp = await client.patch(
        f"/creators/{creator_id}/portfolios/{portfolio_id}/blocks/{block.json()['id']}", json={"position": 5}
    )
    assert resp.json()["position"] == 5


async def test_portfolio_routes_require_auth(unauthenticated_client):
    resp = await unauthenticated_client.post(
        "/creators/11111111-1111-1111-1111-111111111111/portfolios", json={"slug": "x"}
    )
    assert resp.status_code == 401
