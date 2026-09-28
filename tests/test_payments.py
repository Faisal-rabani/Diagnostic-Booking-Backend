import pytest
from datetime import datetime, timedelta

@pytest.fixture
def booking_data(client, auth_headers):
    c_resp = client.post("/api/v1/centres/", json={"name": "C", "location": "L"})
    c_id = c_resp.json()["id"]
    t_resp = client.post("/api/v1/tests/", json={"name": "T", "price": 100.0, "centre_id": c_id})
    t_id = t_resp.json()["id"]
    
    appt_time = (datetime.utcnow() + timedelta(days=1)).isoformat()
    b_resp = client.post(
        "/api/v1/bookings/",
        headers=auth_headers,
        json={
            "test_id": t_id,
            "centre_id": c_id,
            "appointment_time": appt_time
        }
    )
    return {"booking_id": b_resp.json()["id"]}

def test_initiate_payment(client, auth_headers, booking_data):
    response = client.post(
        "/api/v1/payments/",
        headers=auth_headers,
        json={"booking_id": booking_data["booking_id"]}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 100.0
    assert data["status"] == "PENDING"
