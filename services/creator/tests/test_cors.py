"""Vérifie que CORS est bien câblé — sans ça, aucun frontend navigateur ne peut
appeler l'API (voir la question de préparation frontend)."""


async def test_cors_preflight_allows_configured_origin(client):
    resp = await client.options(
        "/creators",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.status_code == 200
    assert resp.headers["access-control-allow-origin"] == "http://localhost:3000"


async def test_cors_actual_response_includes_allow_origin_header(client):
    resp = await client.get("/creators", headers={"Origin": "http://localhost:3000"})
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"
