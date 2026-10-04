from app.schemas.user import UserCreate
from app.services.auth_service import register_user


async def test_create_project(client, auth_headers):
    response = await client.post(
        "/projects", json={"name": "My Project"}, headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["name"] == "My Project"


async def test_create_project_requires_auth(client):
    response = await client.post("/projects", json={"name": "No Auth"})
    assert response.status_code == 401


async def test_list_projects_empty(client, auth_headers):
    response = await client.get("/projects", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


async def test_get_project_not_found(client, auth_headers):
    response = await client.get("/projects/9999", headers=auth_headers)
    assert response.status_code == 404


async def test_update_project(client, auth_headers):
    create = await client.post("/projects", json={"name": "Old"}, headers=auth_headers)
    project_id = create.json()["id"]

    response = await client.patch(
        f"/projects/{project_id}", json={"name": "New"}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New"


async def test_delete_project(client, auth_headers):
    create = await client.post(
        "/projects", json={"name": "To delete"}, headers=auth_headers
    )
    project_id = create.json()["id"]

    delete_response = await client.delete(
        f"/projects/{project_id}", headers=auth_headers
    )
    assert delete_response.status_code == 204

    get_response = await client.get(f"/projects/{project_id}", headers=auth_headers)
    assert get_response.status_code == 404


async def test_cannot_access_other_users_project(client, auth_headers, db_session):
    create = await client.post(
        "/projects", json={"name": "Owner's"}, headers=auth_headers
    )
    project_id = create.json()["id"]

    other_data = UserCreate(email="other@test.com", password="otherpass123")
    await register_user(db_session, other_data)
    login = await client.post(
        "/auth/login", data={"username": "other@test.com", "password": "otherpass123"}
    )
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = await client.get(f"/projects/{project_id}", headers=other_headers)
    assert response.status_code == 403
