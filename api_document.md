# API Documentation

Base URL: `/api/v1`

## Authentication

### 1. Signup
- **Endpoint**: `POST /auth/signup`
- **Description**: Register a new user.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Responses**:
  - `201 Created`: User successfully registered.
  - `400 Bad Request`: Email already exists.

### 2. Login
- **Endpoint**: `POST /auth/login`
- **Description**: Authenticate and receive a JWT.
- **Request Body** (Form Data):
  - `username`: user@example.com
  - `password`: securepassword
- **Responses**:
  - `200 OK`: Returns access token.
  - `401 Unauthorized`: Invalid credentials.

### 3. Get Current User
- **Endpoint**: `GET /auth/me`
- **Description**: Retrieve authenticated user details.
- **Headers**: `Authorization: Bearer <token>`
- **Responses**:
  - `200 OK`: Returns user details.
  - `401 Unauthorized`: Invalid token.

---

## Diagnostic Centres

### 1. Create Centre
- **Endpoint**: `POST /centres/`
- **Description**: Add a new diagnostic centre.
- **Request Body**:
  ```json
  {
    "name": "Apollo Diagnostics",
    "location": "New York"
  }
  ```
- **Responses**:
  - `201 Created`: Centre created.

### 2. List Centres
- **Endpoint**: `GET /centres/`
- **Description**: Retrieve all diagnostic centres.
- **Responses**:
  - `200 OK`: List of centres.

### 3. Get Centre by ID
- **Endpoint**: `GET /centres/{centre_id}`
- **Responses**:
  - `200 OK`: Centre details.
  - `404 Not Found`: Centre does not exist.

---

## Diagnostic Tests

### 1. Create Test
- **Endpoint**: `POST /tests/`
- **Description**: Add a new test to a centre.
- **Request Body**:
  ```json
  {
    "name": "Blood Test",
    "description": "Complete blood count",
    "price": 50.0,
    "centre_id": 1
  }
  ```
- **Responses**:
  - `201 Created`: Test created.
  - `400 Bad Request`: Invalid `centre_id`.

### 2. List Tests
- **Endpoint**: `GET /tests/`
- **Responses**:
  - `200 OK`: List of tests.

---

## Bookings

*(Requires Authentication Header)*

### 1. Create Booking
- **Endpoint**: `POST /bookings/`
- **Request Body**:
  ```json
  {
    "test_id": 1,
    "centre_id": 1,
    "appointment_time": "2026-10-01T10:00:00Z"
  }
  ```
- **Responses**:
  - `201 Created`: Booking created with `PENDING` status.
  - `400 Bad Request`: Test does not belong to centre.

### 2. List User Bookings
- **Endpoint**: `GET /bookings/`
- **Responses**:
  - `200 OK`: List of bookings for the authenticated user.

### 3. Cancel Booking
- **Endpoint**: `POST /bookings/{booking_id}/cancel`
- **Responses**:
  - `200 OK`: Booking cancelled.
  - `400 Bad Request`: Cannot cancel a finalized booking.
  - `403 Forbidden`: Not authorized to cancel this booking.

---

## Payments

*(Requires Authentication Header except for Webhooks)*

### 1. Initiate Payment
- **Endpoint**: `POST /payments/`
- **Description**: Initiate payment for a booking.
- **Request Body**:
  ```json
  {
    "booking_id": 1
  }
  ```
- **Responses**:
  - `201 Created`: Payment record created.
  - `400 Bad Request`: Booking is not in `PENDING` state.

### 2. Payment Webhook
- **Endpoint**: `POST /payments/webhook/`
- **Description**: Simulated payment provider webhook (Idempotent).
- **Request Body**:
  ```json
  {
    "event_id": "evt_12345",
    "booking_id": 1,
    "payment_status": "SUCCESS"
  }
  ```
- **Responses**:
  - `200 OK`: Webhook processed successfully or already processed (idempotent).
  - `400 Bad Request`: Invalid status.
  - `404 Not Found`: Booking not found.
