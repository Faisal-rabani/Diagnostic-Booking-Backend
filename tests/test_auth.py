def test_signup(client):
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": "newuser@example.com", "password": "newpassword"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data

def test_duplicate_signup(client, test_user):
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": test_user["email"], "password": "newpassword"}
    )
    assert response.status_code == 400

def test_login(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user["email"], "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_invalid_login(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user["email"], "password": "wrongpassword"}
    )
    assert response.status_code == 401
    
def test_get_me(client, auth_headers, test_user):
    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["email"]

def test_get_me_no_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
