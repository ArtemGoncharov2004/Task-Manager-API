async def test_create_tag(client):
    response = await client.post("/tags", json={"name": "urgent"})
    assert response.status_code == 201
    assert response.json()["name"] == "urgent"


async def test_create_duplicate_tag_conflict(client):
    await client.post("/tags", json={"name": "bug"})
    response = await client.post("/tags", json={"name": "bug"})
    assert response.status_code == 409


async def test_list_tags(client):
    await client.post("/tags", json={"name": "backend"})
    response = await client.get("/tags")
    names = [tag["name"] for tag in response.json()]
    assert "backend" in names


async def test_delete_tag(client):
    create = await client.post("/tags", json={"name": "temp"})
    tag_id = create.json()["id"]

    delete_response = await client.delete(f"/tags/{tag_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/tags/{tag_id}")
    assert get_response.status_code == 404
