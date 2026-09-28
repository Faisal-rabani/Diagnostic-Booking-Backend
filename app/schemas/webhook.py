from pydantic import BaseModel
from app.models.payment import PaymentStatus

class WebhookPayload(BaseModel):
    event_id: str
    booking_id: int
    payment_status: PaymentStatus
