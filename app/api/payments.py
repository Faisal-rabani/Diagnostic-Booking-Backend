from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus
from app.models.user import User
from app.models.webhook_event import WebhookEvent
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.schemas.webhook import WebhookPayload
from app.dependencies.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def initiate_payment(payment_in: PaymentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    booking = db.query(Booking).filter(Booking.id == payment_in.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to pay for this booking")
        
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Cannot initiate payment for booking in {booking.status} state")
        
    db_payment = Payment(
        booking_id=booking.id,
        amount=booking.amount,
        status=PaymentStatus.PENDING
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@router.post("/webhook/", status_code=status.HTTP_200_OK)
def payment_webhook(payload: WebhookPayload, db: Session = Depends(get_db)):
    # Idempotency check: Have we processed this event_id before?
    event = db.query(WebhookEvent).filter(WebhookEvent.event_id == payload.event_id).with_for_update().first()
    
    if event:
        # Event already processed successfully
        return {"status": "ok", "message": "Event already processed"}
        
    # Start transaction for state transitions
    try:
        # Fetch the booking
        booking = db.query(Booking).filter(Booking.id == payload.booking_id).with_for_update().first()
        if not booking:
            # Save the event as processed with an error status or drop it
            # We must fail gracefully. Since it's a webhook, a 404 might cause retries.
            # It's better to record failure and return 400.
            db.rollback()
            raise HTTPException(status_code=404, detail="Booking not found for this payment event")
            
        # We also want to find a pending payment related to this booking to update it
        payment = db.query(Payment).filter(Payment.booking_id == booking.id, Payment.status == PaymentStatus.PENDING).first()
        
        # Determine booking status transition based on payment webhook status
        if payload.payment_status == PaymentStatus.SUCCESS:
            new_booking_status = BookingStatus.CONFIRMED
        elif payload.payment_status == PaymentStatus.FAILED:
            new_booking_status = BookingStatus.FAILED
        else:
            db.rollback()
            raise HTTPException(status_code=400, detail="Invalid payment status in payload")
            
        # Ensure we don't inappropriately revert state
        # (e.g. if it's already CANCELLED, we might not want to CONFIRM it, but we'll stick to a strict FSM)
        if booking.status in [BookingStatus.CONFIRMED, BookingStatus.CANCELLED]:
            # Don't update booking, but we still record the event as processed
            pass
        else:
            booking.status = new_booking_status
            
        if payment:
            payment.status = payload.payment_status
            
        # Record event
        new_event = WebhookEvent(event_id=payload.event_id, status="PROCESSED")
        db.add(new_event)
        
        db.commit()
        return {"status": "ok", "message": "Webhook processed successfully"}
        
    except IntegrityError:
        # Concurrent processing race condition hit the DB unique constraint
        db.rollback()
        return {"status": "ok", "message": "Event already processed concurrently"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
