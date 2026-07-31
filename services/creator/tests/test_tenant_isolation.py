"""Isolation tenant (SPEC.md) : le tenant A ne doit jamais pouvoir lire ni modifier
les créateurs ou portfolios du tenant B, même en devinant un UUID valide."""


async def test_tenant_cannot_read_another_tenants_creator(client_as, tenant_a, tenant_b):
    client_a = await client_as(tenant_a)
    create_resp = await client_a.post("/creators", json={"display_name": "Tenant A Creator"})
    creator_id = create_resp.json()["id"]

    client_b = await client_as(tenant_b)
    resp = await client_b.get(f"/creators/{creator_id}")
    assert resp.status_code == 404


async def test_tenant_cannot_create_portfolio_for_another_tenants_creator(client_as, tenant_a, tenant_b):
    client_a = await client_as(tenant_a)
    create_resp = await client_a.post("/creators", json={"display_name": "Tenant A Creator"})
    creator_id = create_resp.json()["id"]

    client_b = await client_as(tenant_b)
    resp = await client_b.post(f"/creators/{creator_id}/portfolios", json={"slug": "hijack-attempt"})
    assert resp.status_code == 404


async def test_tenant_cannot_read_another_tenants_portfolio(client_as, tenant_a, tenant_b):
    client_a = await client_as(tenant_a)
    creator = await client_a.post("/creators", json={"display_name": "Tenant A Creator"})
    creator_id = creator.json()["id"]
    create_resp = await client_a.post(f"/creators/{creator_id}/portfolios", json={"slug": "tenant-a-portfolio"})
    portfolio_id = create_resp.json()["id"]

    client_b = await client_as(tenant_b)
    resp = await client_b.get(f"/creators/{creator_id}/portfolios/{portfolio_id}")
    assert resp.status_code == 404  # jamais 403 : ne révèle pas que ça existe pour quelqu'un d'autre


async def test_tenant_cannot_update_another_tenants_portfolio(client_as, tenant_a, tenant_b):
    client_a = await client_as(tenant_a)
    creator = await client_a.post("/creators", json={"display_name": "Tenant A Creator"})
    creator_id = creator.json()["id"]
    create_resp = await client_a.post(f"/creators/{creator_id}/portfolios", json={"slug": "tenant-a-portfolio-2"})
    portfolio_id = create_resp.json()["id"]

    client_b = await client_as(tenant_b)
    resp = await client_b.patch(f"/creators/{creator_id}/portfolios/{portfolio_id}", json={"is_published": True})
    assert resp.status_code == 404


async def test_tenant_cannot_delete_another_tenants_portfolio(client_as, tenant_a, tenant_b):
    client_a = await client_as(tenant_a)
    creator = await client_a.post("/creators", json={"display_name": "Tenant A Creator"})
    creator_id = creator.json()["id"]
    create_resp = await client_a.post(f"/creators/{creator_id}/portfolios", json={"slug": "tenant-a-portfolio-3"})
    portfolio_id = create_resp.json()["id"]

    client_b = await client_as(tenant_b)
    resp = await client_b.delete(f"/creators/{creator_id}/portfolios/{portfolio_id}")
    assert resp.status_code == 404

    # toujours là pour son propriétaire légitime
    still_there = await client_a.get(f"/creators/{creator_id}/portfolios/{portfolio_id}")
    assert still_there.status_code == 200


async def test_tenant_cannot_deauthorize_another_tenants_creator(client_as, tenant_a, tenant_b):
    client_a = await client_as(tenant_a)
    creator = await client_a.post("/creators", json={"display_name": "Tenant A Creator"})
    creator_id = creator.json()["id"]

    client_b = await client_as(tenant_b)
    resp = await client_b.patch(f"/creators/{creator_id}", json={"is_authorized": False})
    assert resp.status_code == 404

    still_authorized = await client_a.get(f"/creators/{creator_id}")
    assert still_authorized.json()["is_authorized"] is True


async def test_list_creators_only_shows_own_tenant(client_as, tenant_a, tenant_b):
    client_a = await client_as(tenant_a)
    await client_a.post("/creators", json={"display_name": "A-Creator"})

    client_b = await client_as(tenant_b)
    await client_b.post("/creators", json={"display_name": "B-Creator"})
    listing = await client_b.get("/creators")
    names = [c["display_name"] for c in listing.json()]
    assert names == ["B-Creator"]
