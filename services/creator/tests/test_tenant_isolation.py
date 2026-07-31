"""Isolation tenant (SPEC.md) : le tenant A ne doit jamais pouvoir lire ni modifier
les données du tenant B, même en devinant un UUID valide."""


async def test_tenant_cannot_read_another_tenants_portfolio(client_as, tenant_a, tenant_b):
    client_a = await client_as(tenant_a)
    create_resp = await client_a.post("/portfolios", json={"slug": "tenant-a-portfolio"})
    portfolio_id = create_resp.json()["id"]

    client_b = await client_as(tenant_b)
    resp = await client_b.get(f"/portfolios/{portfolio_id}")
    assert resp.status_code == 404  # jamais 403 : ne révèle pas que ça existe pour quelqu'un d'autre


async def test_tenant_cannot_update_another_tenants_portfolio(client_as, tenant_a, tenant_b):
    client_a = await client_as(tenant_a)
    create_resp = await client_a.post("/portfolios", json={"slug": "tenant-a-portfolio-2"})
    portfolio_id = create_resp.json()["id"]

    client_b = await client_as(tenant_b)
    resp = await client_b.patch(f"/portfolios/{portfolio_id}", json={"is_published": True})
    assert resp.status_code == 404


async def test_tenant_cannot_delete_another_tenants_portfolio(client_as, tenant_a, tenant_b):
    client_a = await client_as(tenant_a)
    create_resp = await client_a.post("/portfolios", json={"slug": "tenant-a-portfolio-3"})
    portfolio_id = create_resp.json()["id"]

    client_b = await client_as(tenant_b)
    resp = await client_b.delete(f"/portfolios/{portfolio_id}")
    assert resp.status_code == 404

    # toujours là pour son propriétaire légitime
    still_there = await client_a.get(f"/portfolios/{portfolio_id}")
    assert still_there.status_code == 200


async def test_tenants_have_independent_creator_profiles(client_as, tenant_a, tenant_b):
    client_a = await client_as(tenant_a)
    await client_a.patch("/creators/me", json={"display_name": "Tenant A"})

    client_b = await client_as(tenant_b)
    resp = await client_b.get("/creators/me")
    assert resp.status_code == 404  # profil du tenant A invisible au tenant B


async def test_list_portfolios_only_shows_own_tenant(client_as, tenant_a, tenant_b):
    client_a = await client_as(tenant_a)
    await client_a.post("/portfolios", json={"slug": "a-only"})

    client_b = await client_as(tenant_b)
    await client_b.post("/portfolios", json={"slug": "b-only"})
    listing = await client_b.get("/portfolios")
    slugs = [p["slug"] for p in listing.json()]
    assert slugs == ["b-only"]
