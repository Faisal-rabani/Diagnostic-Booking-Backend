import pytest
from datetime import datetime, timedelta

@pytest.fixture
def test_data(client):
    c_resp = client.post("/api/v1/centres/", json={"name": "C", "location": "L"})
    c_id = c_resp.json()["id"]
    t_resp = client.post("/api/v1/tests/", json={"name": "T", "price": 100.0, "centre_id": c_id})
    t_id = t_resp.json()["id"]
    
    # Create another centre
    c2_resp = client.post("/api/v1/centres/", json={"name": "C2", "location": "L2"})
    c2_id = c2_resp.json()["id"]
    
    return {"centre_id": c_id, "test_id": t_id, "other_centre_id": c2_id}

def test_create_booking(client, auth_headers, test_data):
    appt_time = (datetime.utcnow() + timedelta(days=1)).isoformat()
    response = client.post(
        "/api/v1/bookings/",
        headers=auth_headers,
        json={
            "test_id": test_data["test_id"],
            "centre_id": test_data["centre_id"],
            "appointment_time": appt_time
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 100.0
    assert data["status"] == "PENDING"
    assert "id" in data

def test_create_booking_invalid_centre(client, auth_headers, test_data):
    appt_time = (datetime.utcnow() + timedelta(days=1)).isoformat()
    response = client.post(
        "/api/v1/bookings/",
        headers=auth_headers,
        json={
            "test_id": test_data["test_id"],
            "centre_id": test_data["other_centre_id"],
            "appointment_time": appt_time
        }
    )
    assert response.status_code == 400
    assert "Test does not belong to the specified centre" in response.json()["detail"]

def test_create_booking_unauthorized(client, test_data):
    appt_time = (datetime.utcnow() + timedelta(days=1)).isoformat()
    response = client.post(
        "/api/v1/bookings/",
        json={
            "test_id": test_data["test_id"],
            "centre_id": test_data["centre_id"],
            "appointment_time": appt_time
        }
    )
    assert response.status_code == 401
