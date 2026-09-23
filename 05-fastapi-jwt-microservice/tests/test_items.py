"""
Integration tests for Items CRUD endpoints and ownership access controls.
"""


def _get_auth_headers(client, email="item_owner@example.com"):
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": "Item Owner"},
    )
    res = client.post(
        "/api/v1/auth/login/json",
        json={"email": email, "password": "Password123!"},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_items_crud_lifecycle(client):
    headers = _get_auth_headers(client, "user_crud@example.com")

    # 1. Create
    create_res = client.post(
        "/api/v1/items/",
        headers=headers,
        json={
            "title": "Configure CI/CD Pipelines",
            "description": "Set up automated GitHub actions and tests",
            "priority": "HIGH",
            "status": "PENDING",
        },
    )
    assert create_res.status_code == 201
    item = create_res.json()
    item_id = item["id"]
    assert item["title"] == "Configure CI/CD Pipelines"
    assert item["priority"] == "HIGH"

    # 2. List
    list_res = client.get("/api/v1/items/", headers=headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] == 1
    assert len(list_res.json()["items"]) == 1

    # 3. Read Single
    read_res = client.get(f"/api/v1/items/{item_id}", headers=headers)
    assert read_res.status_code == 200
    assert read_res.json()["id"] == item_id

    # 4. Update
    update_res = client.put(
        f"/api/v1/items/{item_id}",
        headers=headers,
        json={"status": "COMPLETED"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "COMPLETED"

    # 5. Delete
    del_res = client.delete(f"/api/v1/items/{item_id}", headers=headers)
    assert del_res.status_code == 204

    # 6. Verify Deleted
    get_del = client.get(f"/api/v1/items/{item_id}", headers=headers)
    assert get_del.status_code == 404


def test_cross_user_isolation(client):
    user1_headers = _get_auth_headers(client, "user_one@example.com")
    user2_headers = _get_auth_headers(client, "user_two@example.com")

    # User 1 creates an item
    res = client.post(
        "/api/v1/items/",
        headers=user1_headers,
        json={"title": "Private Secret Item", "priority": "URGENT"},
    )
    item_id = res.json()["id"]

    # User 2 attempts to read User 1's item
    read_res = client.get(f"/api/v1/items/{item_id}", headers=user2_headers)
    assert read_res.status_code == 403

    # User 2 attempts to update User 1's item
    update_res = client.put(f"/api/v1/items/{item_id}", headers=user2_headers, json={"title": "Hacked"})
    assert update_res.status_code == 403

    # User 2 attempts to delete User 1's item
    del_res = client.delete(f"/api/v1/items/{item_id}", headers=user2_headers)
    assert del_res.status_code == 403


def test_unauthorized_access(client):
    res = client.get("/api/v1/items/")
    assert res.status_code == 401
