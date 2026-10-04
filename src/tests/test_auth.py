async def test_register_user(client):
    response = await client.post(
        "/auth/register",
        json={"email": "newuser@test.com", "password": "securepass123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert "password" not in data


async def test_register_duplicate_email(client, test_user):
    user, _ = test_user
    response = await client.post(
        "/auth/register",
        json={"email": user.email, "password": "anotherpass123"},
    )
    assert response.status_code == 409


async def test_login_success(client, test_user):
    user, password = test_user
    response = await client.post(
        "/auth/login",
        data={"username": user.email, "password": password},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client, test_user):
    user, _ = test_user
    response = await client.post(
        "/auth/login",
        data={"username": user.email, "password": "wrongpassword"},
    )
    assert response.status_code == 401


async def test_login_nonexistent_user(client):
    response = await client.post(
        "/auth/login",
        data={"username": "ghost@test.com", "password": "whatever123"},
    )
    assert response.status_code == 401
