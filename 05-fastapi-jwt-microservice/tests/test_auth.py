"""
Integration tests for User Authentication endpoints.
"""


def test_register_user_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "developer@example.com",
            "password": "Password123!",
            "full_name": "Dev User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "developer@example.com"
    assert data["full_name"] == "Dev User"
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "dupe@example.com", "password": "Password123!"},
    )
    # Duplicate attempt
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "dupe@example.com", "password": "AnotherPassword123!"},
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_oauth2_form_and_json(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "login_user@example.com", "password": "ValidPassword123!"},
    )

    # 1. Test OAuth2 form login
    response_form = client.post(
        "/api/v1/auth/login",
        data={"username": "login_user@example.com", "password": "ValidPassword123!"},
    )
    assert response_form.status_code == 200
    assert "access_token" in response_form.json()

    # 2. Test JSON login
    response_json = client.post(
        "/api/v1/auth/login/json",
        json={"email": "login_user@example.com", "password": "ValidPassword123!"},
    )
    assert response_json.status_code == 200
    assert "access_token" in response_json.json()


def test_login_invalid_password(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "target@example.com", "password": "CorrectPassword123!"},
    )
    response = client.post(
        "/api/v1/auth/login/json",
        json={"email": "target@example.com", "password": "WrongPassword123!"},
    )
    assert response.status_code == 401


def test_read_me_endpoint(client):
    # Register & Login
    client.post(
        "/api/v1/auth/register",
        json={"email": "me_user@example.com", "password": "Password123!", "full_name": "Me User"},
    )
    login_res = client.post(
        "/api/v1/auth/login/json",
        json={"email": "me_user@example.com", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]

    # Authenticated call
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "me_user@example.com"

    # Unauthenticated call
    unauth_res = client.get("/api/v1/auth/me")
    assert unauth_res.status_code == 401
