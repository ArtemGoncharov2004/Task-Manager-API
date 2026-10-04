from app.schemas.user import UserCreate
from app.services.auth_service import register_user


async def test_create_task(client, auth_headers, test_project):
    response = await client.post(
        "/tasks",
        json={"title": "Write tests", "project_id": test_project["id"]},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "todo"
    assert data["priority"] == 3


async def test_create_task_in_foreign_project_forbidden(
    client, auth_headers, db_session, test_project
):
    other_data = UserCreate(email="other2@test.com", password="otherpass123")
    await register_user(db_session, other_data)
    login = await client.post(
        "/auth/login", data={"username": "other2@test.com", "password": "otherpass123"}
    )
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = await client.post(
        "/tasks",
        json={"title": "Sneaky task", "project_id": test_project["id"]},
        headers=other_headers,
    )
    assert response.status_code == 403


async def test_list_tasks_status_filter(client, auth_headers, test_project):
    await client.post(
        "/tasks",
        json={"title": "Todo", "project_id": test_project["id"], "status": "todo"},
        headers=auth_headers,
    )
    await client.post(
        "/tasks",
        json={"title": "Done", "project_id": test_project["id"], "status": "done"},
        headers=auth_headers,
    )

    response = await client.get("/tasks?status=done", headers=auth_headers)
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Done"


async def test_list_tasks_pagination(client, auth_headers, test_project):
    for i in range(5):
        await client.post(
            "/tasks",
            json={"title": f"Task {i}", "project_id": test_project["id"]},
            headers=auth_headers,
        )

    response = await client.get("/tasks?skip=0&limit=2", headers=auth_headers)
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5


async def test_update_task_status(client, auth_headers, test_project):
    create = await client.post(
        "/tasks",
        json={"title": "To update", "project_id": test_project["id"]},
        headers=auth_headers,
    )
    task_id = create.json()["id"]

    response = await client.patch(
        f"/tasks/{task_id}", json={"status": "in_progress"}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


async def test_delete_task(client, auth_headers, test_project):
    create = await client.post(
        "/tasks",
        json={"title": "To delete", "project_id": test_project["id"]},
        headers=auth_headers,
    )
    task_id = create.json()["id"]

    delete_response = await client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    get_response = await client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 404


async def test_invalid_priority_rejected(client, auth_headers, test_project):
    response = await client.post(
        "/tasks",
        json={
            "title": "Bad priority",
            "project_id": test_project["id"],
            "priority": 10,
        },
        headers=auth_headers,
    )
    assert response.status_code == 422
