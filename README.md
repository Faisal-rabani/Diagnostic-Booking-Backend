![Healthcare Booking Service Banner](docs/banner.jpg)

# Healthcare Booking Service API

## Project Overview
Welcome to the **Healthcare Booking Service**, a robust, production-ready backend service designed for the EVE Healthcare SDE Intern Backend Engineering Assignment. 

Built with scalability and data integrity in mind, this RESTful API handles end-to-end diagnostic centre management, secure patient test bookings, and a highly resilient, idempotent simulated payment processing pipeline. The architecture strictly enforces state transitions, relational integrity, and flawless duplicate webhook handling.

## Features
- **User Authentication**: Secure signup and login using JWT and bcrypt.
- **Diagnostic Centres & Tests**: Browse centres and their available diagnostic tests.
- **Booking Flow**: Users can book tests with state management (`PENDING`, `CONFIRMED`, `FAILED`, `CANCELLED`).
- **Simulated Payments**: Initiate payments for pending bookings.
- **Idempotent Webhooks**: Robust simulated payment webhook endpoint that guarantees safe processing even if identical events are received concurrently or repeatedly.
- **Edge Case Handling**: Extensive validation and exception handling.

## Technology Stack
- **Backend**: Python 3.11, FastAPI
- **Database**: PostgreSQL (SQLAlchemy ORM, async-capable setup but currently synchronous for simplicity and robustness in this assignment)
- **Migrations**: Alembic
- **Testing**: pytest, HTTPX (FastAPI TestClient)
- **Containerization**: Docker, docker-compose

## Architecture
The project follows a modular monolith architecture, separating concerns across different directories:
- `app/api/`: API Routers for grouping endpoints.
- `app/core/`: Configuration, security, and database setup.
- `app/models/`: SQLAlchemy ORM database models.
- `app/schemas/`: Pydantic validation schemas.
- `app/dependencies/`: Reusable FastAPI dependencies (e.g. `get_current_user`).
- `tests/`: Extensive test suite mimicking real-world constraints.

## Folder Structure
```
app/
├── main.py
├── core/
│   ├── config.py
│   ├── security.py
│   └── database.py
├── models/
│   ├── user.py
│   ├── diagnostic_centre.py
│   ├── diagnostic_test.py
│   ├── booking.py
│   ├── payment.py
│   └── webhook_event.py
├── schemas/
│   ├── auth.py
│   ├── user.py
│   ├── diagnostic_centre.py
│   ├── diagnostic_test.py
│   ├── booking.py
│   ├── payment.py
│   └── webhook.py
├── api/
│   ├── auth.py
│   ├── centres.py
│   ├── tests.py
│   ├── bookings.py
│   └── payments.py
├── dependencies/
│   └── auth.py
tests/
├── conftest.py
├── test_auth.py
├── ...
alembic/
├── versions/
├── env.py
Dockerfile
docker-compose.yml
requirements.txt
```

## Setup Instructions & Environment Variables
Copy the sample environment file to `.env` and fill it with appropriate values.
```bash
cp .env.example .env
```

**Environment Variables**:
- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql://postgres:postgres@db:5432/healthcare_booking`)
- `SECRET_KEY`: A strong random string for JWT encoding.
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: PostgreSQL credentials.

## How to Run Locally (Docker)
The easiest way to run the application and database together is using Docker Compose.
```bash
docker-compose up --build
```
This will start the API on `http://localhost:8000` and the database on `5432`.

## Database Migration Commands
To initialize the database tables inside the docker container (if running locally without docker, run these with your venv active):
```bash
docker-compose exec api alembic upgrade head
```

## Important Assumptions
1. We simulate payments synchronously by just marking a payment as pending, then the mock provider hits our webhook.
2. We assume the webhook sends the `booking_id` in its payload to uniquely identify which booking to update.
3. Tests use SQLite in-memory DB for speed and isolation, as the simple relational data models used do not strictly require PostgreSQL specific types.

## Idempotency Strategy
The system uses the `WebhookEvent` model with a unique constraint on `event_id`. When a webhook arrives:
1. We try to query the event with a `FOR UPDATE` lock.
2. If it exists, we return a success response immediately (idempotent).
3. We fetch the `Booking` with a `FOR UPDATE` lock.
4. We apply state transitions.
5. We insert the `WebhookEvent` to record the event.
6. A Database `IntegrityError` is explicitly caught to handle the unlikely edge case where a concurrent webhook inserts the same `event_id` between our lock and commit, safely rolling back.

## Testing Instructions & Report
We have verified the implementation using an extensive automated testing suite. Please see the [Test Report](test_report.md) for a detailed breakdown of all the test results which validates the core constraints, webhook idempotency, and the simulated payment cycle.

To run the automated tests locally:
```bash
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
pytest -v
```

## API Documentation
Once the server is running, visit `http://localhost:8000/api/v1/openapi.json` for the raw schema, or `http://localhost:8000/docs` for the interactive Swagger documentation.
