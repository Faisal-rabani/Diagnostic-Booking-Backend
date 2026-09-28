import pytest
from datetime import datetime, timedelta

@pytest.fixture
def webhook_test_data(client, auth_headers):
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
    booking_id = b_resp.json()["id"]
    
    p_resp = client.post(
        "/api/v1/payments/",
        headers=auth_headers,
        json={"booking_id": booking_id}
    )
    payment_id = p_resp.json()["id"]
    
    return {"booking_id": booking_id, "payment_id": payment_id}

def test_webhook_success(client, auth_headers, webhook_test_data):
    event_id = "evt_12345"
    response = client.post(
        "/api/v1/payments/webhook/",
        json={
            "event_id": event_id,
            "booking_id": webhook_test_data["booking_id"],
            "payment_status": "SUCCESS"
        }
    )
    assert response.status_code == 200
    
    # Check booking status
    b_resp = client.get(f"/api/v1/bookings/{webhook_test_data['booking_id']}", headers=auth_headers)
    assert b_resp.json()["status"] == "CONFIRMED"

def test_webhook_idempotency(client, auth_headers, webhook_test_data):
    event_id = "evt_idempotent_1"
    
    # First call
    response1 = client.post(
        "/api/v1/payments/webhook/",
        json={
            "event_id": event_id,
            "booking_id": webhook_test_data["booking_id"],
            "payment_status": "SUCCESS"
        }
    )
    assert response1.status_code == 200
    
    # Check booking status
    b_resp1 = client.get(f"/api/v1/bookings/{webhook_test_data['booking_id']}", headers=auth_headers)
    assert b_resp1.json()["status"] == "CONFIRMED"
    
    # Second call with the same event ID
    response2 = client.post(
        "/api/v1/payments/webhook/",
        json={
            "event_id": event_id,
            "booking_id": webhook_test_data["booking_id"],
            "payment_status": "FAILED" # Changing status to simulate weird webhook, but it should be ignored!
        }
    )
    assert response2.status_code == 200
    assert response2.json()["message"] == "Event already processed"
    
    # Check booking status remains CONFIRMED
    b_resp2 = client.get(f"/api/v1/bookings/{webhook_test_data['booking_id']}", headers=auth_headers)
    assert b_resp2.json()["status"] == "CONFIRMED"
