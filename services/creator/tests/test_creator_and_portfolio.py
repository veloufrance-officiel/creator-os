"""Tests bout-en-bout via l'API — voir SPEC.md pour la liste des scénarios."""


async def test_upsert_creator_creates_then_updates(client):
    create_resp = await client.patch("/creators/me", json={"display_name": "Ada", "niche": "tech"})
    assert create_resp.status_code == 200
    assert create_resp.json()["display_name"] == "Ada"

    update_resp = await client.patch("/creators/me", json={"display_name": "Ada L.", "niche": "tech"})
    assert update_resp.status_code == 200
    assert update_resp.json()["display_name"] == "Ada L."
    assert update_resp.json()["id"] == create_resp.json()["id"]  # même profil, pas un doublon


async def test_get_me_404_before_any_upsert(client):
    resp = await client.get("/creators/me")
    assert resp.status_code == 404


async def test_creators_me_requires_auth(unauthenticated_client):
    resp = await unauthenticated_client.get("/creators/me")
    assert resp.status_code == 401


async def test_portfolio_not_published_by_default(client):
    resp = await client.post("/portfolios", json={"slug": "ada-portfolio", "title": "Ada"})
    assert resp.status_code == 201
    assert resp.json()["is_published"] is False  # Privacy By Default, ADR-0003


async def test_duplicate_slug_conflicts(client):
    await client.post("/portfolios", json={"slug": "taken-slug"})
    resp = await client.post("/portfolios", json={"slug": "taken-slug"})
    assert resp.status_code == 409


async def test_public_portfolio_404_when_not_published(client):
    create_resp = await client.post("/portfolios", json={"slug": "private-one"})
    assert create_resp.json()["is_published"] is False

    resp = await client.get("/public/portfolios/private-one")
    assert resp.status_code == 404


async def test_public_portfolio_404_when_slug_does_not_exist(client):
    resp = await client.get("/public/portfolios/does-not-exist")
    assert resp.status_code == 404


async def test_publishing_makes_portfolio_publicly_visible(client):
    create_resp = await client.post("/portfolios", json={"slug": "now-public", "title": "Public Me"})
    portfolio_id = create_resp.json()["id"]

    await client.patch(f"/portfolios/{portfolio_id}", json={"is_published": True})

    resp = await client.get("/public/portfolios/now-public")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Public Me"


async def test_blocks_created_updated_deleted(client):
    create_resp = await client.post("/portfolios", json={"slug": "block-test"})
    portfolio_id = create_resp.json()["id"]

    add_resp = await client.post(
        f"/portfolios/{portfolio_id}/blocks", json={"type": "bio", "config": {"text": "hello"}}
    )
    assert add_resp.status_code == 201
    block_id = add_resp.json()["id"]
    assert add_resp.json()["position"] == 0

    update_resp = await client.patch(
        f"/portfolios/{portfolio_id}/blocks/{block_id}", json={"config": {"text": "updated"}}
    )
    assert update_resp.json()["config"]["text"] == "updated"

    delete_resp = await client.delete(f"/portfolios/{portfolio_id}/blocks/{block_id}")
    assert delete_resp.status_code == 204

    portfolio_resp = await client.get(f"/portfolios/{portfolio_id}")
    assert portfolio_resp.json()["blocks"] == []


async def test_blocks_auto_increment_position(client):
    create_resp = await client.post("/portfolios", json={"slug": "position-test"})
    portfolio_id = create_resp.json()["id"]

    first = await client.post(f"/portfolios/{portfolio_id}/blocks", json={"type": "bio", "config": {}})
    second = await client.post(f"/portfolios/{portfolio_id}/blocks", json={"type": "links", "config": {}})

    assert first.json()["position"] == 0
    assert second.json()["position"] == 1


async def test_reorder_block_via_explicit_position(client):
    create_resp = await client.post("/portfolios", json={"slug": "reorder-test"})
    portfolio_id = create_resp.json()["id"]
    block = await client.post(f"/portfolios/{portfolio_id}/blocks", json={"type": "bio", "config": {}})

    resp = await client.patch(f"/portfolios/{portfolio_id}/blocks/{block.json()['id']}", json={"position": 5})
    assert resp.json()["position"] == 5


async def test_portfolio_routes_require_auth(unauthenticated_client):
    resp = await unauthenticated_client.post("/portfolios", json={"slug": "x"})
    assert resp.status_code == 401
