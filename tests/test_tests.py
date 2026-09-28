import pytest

@pytest.fixture
def test_centre(client):
    resp = client.post("/api/v1/centres/", json={"name": "Test Centre", "location": "Loc"})
    return resp.json()

def test_create_test(client, test_centre):
    response = client.post(
        "/api/v1/tests/",
        json={
            "name": "Blood Test",
            "description": "Basic blood panel",
            "price": 50.0,
            "centre_id": test_centre["id"]
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Blood Test"
    assert data["price"] == 50.0
    assert data["centre_id"] == test_centre["id"]

def test_create_test_invalid_centre(client):
    response = client.post(
        "/api/v1/tests/",
        json={
            "name": "Blood Test",
            "price": 50.0,
            "centre_id": 9999
        }
    )
    assert response.status_code == 400

def test_get_tests(client, test_centre):
    client.post("/api/v1/tests/", json={"name": "T1", "price": 10.0, "centre_id": test_centre["id"]})
    response = client.get("/api/v1/tests/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
