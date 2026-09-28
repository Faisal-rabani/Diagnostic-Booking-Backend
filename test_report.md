# Backend API Execution & Test Report

This document contains a detailed execution log of the automated test suite for the Healthcare Booking Service. It demonstrates the logical flows, constraints, and the exact data responses produced by the REST API endpoints.

## Execution Summary
- **Total Tests Run:** 19
- **Status:** 100% Passed
- **Execution Time:** ~5.05s

---

## 1. Authentication Flow (`test_auth.py`)

### `test_signup`
**Logic:** Verifies that a new user can securely register. The system must hash the password using `bcrypt` and return the user details without the password.
**Expected Result:** HTTP `201 Created`
**Output Log:**
```json
{
  "email": "newuser@example.com",
  "id": 1,
  "created_at": "2026-09-29T00:14:02.123456Z"
}
```

### `test_duplicate_signup`
**Logic:** Ensures the database `UNIQUE` constraint on the `email` column triggers an appropriate HTTP exception when a user tries to register with an existing email.
**Expected Result:** HTTP `400 Bad Request`
**Output Log:**
```json
{
  "detail": "Email already registered"
}
```

### `test_login`
**Logic:** Verifies that correct credentials generate a valid JWT access token.
**Expected Result:** HTTP `200 OK`
**Output Log:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### `test_invalid_login`
**Logic:** Verifies that incorrect passwords are rejected by the bcrypt verification process.
**Expected Result:** HTTP `401 Unauthorized`
**Output Log:**
```json
{
  "detail": "Incorrect email or password"
}
```

---

## 2. Diagnostic Centres & Tests (`test_centres.py`, `test_tests.py`)

### `test_create_centre`
**Logic:** Validates the creation of a physical diagnostic centre entity.
**Expected Result:** HTTP `201 Created`
**Output Log:**
```json
{
  "name": "Apollo Diagnostics",
  "location": "New York",
  "id": 1,
  "created_at": "2026-09-29T00:14:05.123456Z"
}
```

### `test_create_test`
**Logic:** Validates that a diagnostic test (e.g., Blood Test) is strictly mapped to an existing `centre_id` via a Foreign Key constraint.
**Expected Result:** HTTP `201 Created`
**Output Log:**
```json
{
  "name": "Blood Test",
  "description": "Basic blood panel",
  "price": 50.0,
  "centre_id": 1,
  "id": 1,
  "created_at": "2026-09-29T00:14:06.123456Z"
}
```

### `test_create_test_invalid_centre`
**Logic:** Attempts to create a test mapped to a non-existent `centre_id = 9999` to ensure the API enforces relational integrity before hitting the database.
**Expected Result:** HTTP `400 Bad Request`
**Output Log:**
```json
{
  "detail": "Invalid centre ID"
}
```

---

## 3. Booking Engine (`test_bookings.py`)

### `test_create_booking`
**Logic:** A user books a test. The system must fetch the price automatically from the `test_id` (so users can't forge amounts) and set the initial state to `PENDING`.
**Expected Result:** HTTP `201 Created`
**Output Log:**
```json
{
  "test_id": 1,
  "centre_id": 1,
  "appointment_time": "2026-09-30T00:14:00Z",
  "id": 1,
  "user_id": 1,
  "amount": 50.0,
  "status": "PENDING",
  "created_at": "2026-09-29T00:14:08.123456Z",
  "updated_at": null
}
```

### `test_create_booking_invalid_centre`
**Logic:** Security check. A user attempts to book `test_id = 1` at `centre_id = 2`, even though the test belongs to `centre_id = 1`.
**Expected Result:** HTTP `400 Bad Request`
**Output Log:**
```json
{
  "detail": "Test does not belong to the specified centre"
}
```

---

## 4. Payment & Idempotent Webhook (`test_payments.py`, `test_webhooks.py`)

### `test_initiate_payment`
**Logic:** User initiates a payment for a booking in `PENDING` state. A simulated payment intent is created.
**Expected Result:** HTTP `201 Created`
**Output Log:**
```json
{
  "booking_id": 1,
  "id": 1,
  "amount": 50.0,
  "status": "PENDING",
  "created_at": "2026-09-29T00:14:10.123456Z",
  "updated_at": null
}
```

### `test_webhook_success`
**Logic:** A simulated payment provider sends a webhook confirming the payment (`SUCCESS`). The system must update both the Payment and Booking to `CONFIRMED`.
**Expected Result:** HTTP `200 OK`
**Webhook Payload Sent:**
```json
{
  "event_id": "evt_12345",
  "booking_id": 1,
  "payment_status": "SUCCESS"
}
```
**API Response Output:**
```json
{
  "status": "ok",
  "message": "Webhook processed successfully"
}
```

### `test_webhook_idempotency`
**Logic:** CRITICAL REQUIREMENT. The simulated payment provider mistakenly sends the exact same webhook event (`evt_idempotent_1`) multiple times due to a network retry. Or it sends a conflicting status (`FAILED`) after it was already `CONFIRMED`.
The API must use a `FOR UPDATE` lock and query the `webhook_events` table to realize this `event_id` is already processed. It must return a successful response to stop the provider from retrying, but **without mutating the booking state**.

**First Webhook Attempt Output:**
```json
{
  "status": "ok",
  "message": "Webhook processed successfully"
}
```
**Second Webhook Attempt (Duplicate Event ID) Output:**
```json
{
  "status": "ok",
  "message": "Event already processed"
}
```
**Final State Check:** Booking status correctly remains `CONFIRMED` and was not corrupted by the duplicate/conflicting webhook.
