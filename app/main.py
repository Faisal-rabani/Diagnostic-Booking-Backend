from fastapi import FastAPI
from app.core.config import settings

from app.api.auth import router as auth_router
from app.api.centres import router as centres_router
from app.api.tests import router as tests_router
from app.api.bookings import router as bookings_router
from app.api.payments import router as payments_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(centres_router, prefix=f"{settings.API_V1_STR}/centres", tags=["centres"])
app.include_router(tests_router, prefix=f"{settings.API_V1_STR}/tests", tags=["tests"])
app.include_router(bookings_router, prefix=f"{settings.API_V1_STR}/bookings", tags=["bookings"])
app.include_router(payments_router, prefix=f"{settings.API_V1_STR}/payments", tags=["payments"])

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
