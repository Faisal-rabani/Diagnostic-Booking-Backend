from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.diagnostic_test import DiagnosticTest
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingResponse
from app.dependencies.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(booking_in: BookingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    test = db.query(DiagnosticTest).filter(DiagnosticTest.id == booking_in.test_id).first()
    if not test:
        raise HTTPException(status_code=400, detail="Invalid test ID")
    
    if test.centre_id != booking_in.centre_id:
        raise HTTPException(status_code=400, detail="Test does not belong to the specified centre")
    
    db_booking = Booking(
        user_id=current_user.id,
        test_id=booking_in.test_id,
        centre_id=booking_in.centre_id,
        appointment_time=booking_in.appointment_time,
        amount=test.price,
        status=BookingStatus.PENDING
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@router.get("/", response_model=List[BookingResponse])
def get_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bookings = db.query(Booking).filter(Booking.user_id == current_user.id).offset(skip).limit(limit).all()
    return bookings

@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this booking")
    return booking

@router.post("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this booking")
    
    if booking.status in [BookingStatus.CONFIRMED, BookingStatus.FAILED, BookingStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel a booking in {booking.status} state")
        
    booking.status = BookingStatus.CANCELLED
    db.commit()
    db.refresh(booking)
    return booking
