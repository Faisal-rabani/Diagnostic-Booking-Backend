from pydantic import BaseModel
from datetime import datetime
from app.models.booking import BookingStatus

class BookingBase(BaseModel):
    test_id: int
    centre_id: int
    appointment_time: datetime

class BookingCreate(BookingBase):
    pass

class BookingResponse(BookingBase):
    id: int
    user_id: int
    amount: float
    status: BookingStatus
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
