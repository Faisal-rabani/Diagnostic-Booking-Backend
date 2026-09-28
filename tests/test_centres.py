def test_create_centre(client):
    response = client.post(
        "/api/v1/centres/",
        json={"name": "Apollo Diagnostics", "location": "New York"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Apollo Diagnostics"
    assert "id" in data

def test_get_centres(client):
    client.post("/api/v1/centres/", json={"name": "C1", "location": "L1"})
    client.post("/api/v1/centres/", json={"name": "C2", "location": "L2"})
    
    response = client.get("/api/v1/centres/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

def test_get_centre(client):
    create_resp = client.post("/api/v1/centres/", json={"name": "C3", "location": "L3"})
    c_id = create_resp.json()["id"]
    
    response = client.get(f"/api/v1/centres/{c_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "C3"

def test_get_centre_not_found(client):
    response = client.get("/api/v1/centres/9999")
    assert response.status_code == 404
