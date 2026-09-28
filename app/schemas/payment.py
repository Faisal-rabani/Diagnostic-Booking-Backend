from pydantic import BaseModel
from datetime import datetime
from app.models.payment import PaymentStatus

class PaymentBase(BaseModel):
    booking_id: int

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: int
    amount: float
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
