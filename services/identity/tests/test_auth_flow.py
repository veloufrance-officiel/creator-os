"""Tests bout-en-bout via l'API (httpx + ASGITransport) — voir SPEC.md pour la liste.
Choix : tester par le contrat HTTP plutôt que les fonctions internes, pour vérifier
ce qu'un vrai client verrait (statuts, formes de réponse), pas l'implémentation."""


async def test_register_creates_account_and_returns_tokens(client, registered_user_payload):
    resp = await client.post("/auth/register", json=registered_user_payload)
    assert resp.status_code == 201
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body


async def test_register_twice_same_email_conflicts(client, registered_user_payload):
    await client.post("/auth/register", json=registered_user_payload)
    resp = await client.post("/auth/register", json=registered_user_payload)
    assert resp.status_code == 409


async def test_login_success(client, registered_user_payload):
    await client.post("/auth/register", json=registered_user_payload)
    resp = await client.post("/auth/login", json=registered_user_payload)
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_login_wrong_password_returns_generic_401(client, registered_user_payload):
    await client.post("/auth/register", json=registered_user_payload)
    resp = await client.post(
        "/auth/login", json={"email": registered_user_payload["email"], "password": "wrong-password"}
    )
    assert resp.status_code == 401
    # Message générique : ne doit pas révéler si c'est l'email ou le mot de passe (SPEC.md)
    assert "incorrect" in resp.json()["detail"].lower()


async def test_login_unknown_email_returns_same_generic_401(client):
    resp = await client.post("/auth/login", json={"email": "inconnu@nowhere.dev", "password": "whatever123"})
    assert resp.status_code == 401
    assert "incorrect" in resp.json()["detail"].lower()


async def test_me_requires_authentication(client):
    resp = await client.get("/me")
    assert resp.status_code == 401


async def test_me_returns_current_user_profile(client, registered_user_payload):
    register_resp = await client.post("/auth/register", json=registered_user_payload)
    access_token = register_resp.json()["access_token"]

    resp = await client.get("/me", headers={"Authorization": f"Bearer {access_token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == registered_user_payload["email"]
    assert "owner" in body["roles"]


async def test_refresh_rotates_session(client, registered_user_payload):
    register_resp = await client.post("/auth/register", json=registered_user_payload)
    old_refresh = register_resp.json()["refresh_token"]

    resp = await client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert resp.status_code == 200
    new_tokens = resp.json()
    assert new_tokens["refresh_token"] != old_refresh

    # L'ancien refresh token ne doit plus être utilisable (rotation, voir SPEC.md)
    replay = await client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert replay.status_code == 401


async def test_refresh_with_garbage_token_returns_401(client):
    resp = await client.post("/auth/refresh", json={"refresh_token": "not-a-real-token"})
    assert resp.status_code == 401


async def test_logout_revokes_session(client, registered_user_payload):
    register_resp = await client.post("/auth/register", json=registered_user_payload)
    refresh_token = register_resp.json()["refresh_token"]

    logout_resp = await client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert logout_resp.status_code == 204

    reuse = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert reuse.status_code == 401


async def test_audit_logs_requires_permission(client):
    resp = await client.get("/audit-logs")
    assert resp.status_code == 401  # pas de token du tout


async def test_audit_logs_accessible_to_owner_and_contains_register_event(client, registered_user_payload):
    register_resp = await client.post("/auth/register", json=registered_user_payload)
    access_token = register_resp.json()["access_token"]

    resp = await client.get("/audit-logs", headers={"Authorization": f"Bearer {access_token}"})
    assert resp.status_code == 200
    actions = [entry["action"] for entry in resp.json()]
    assert "user.register" in actions


async def test_password_too_short_is_rejected(client):
    resp = await client.post("/auth/register", json={"email": "short@creator-os.dev", "password": "short"})
    assert resp.status_code == 422
