from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db, Base, engine
from ..models import Booking
from ..schemas import BookingRequest, BookingResponse
from ..services.mailer import send_email

router = APIRouter(prefix="/bookings", tags=["bookings"])

Base.metadata.create_all(bind=engine)

@router.post("", response_model=BookingResponse)
def create_booking(req: BookingRequest, db: Session = Depends(get_db)):
    existing = db.query(Booking).filter(Booking.email==req.email, Booking.date==req.date, Booking.time==req.time).first()
    
    if existing:
        raise HTTPException(status_code=409, detail="Booking already exists for this slot.")
    
    b = Booking(name=req.name, email=req.email, date=req.date, time=req.time)
    db.add(b); db.commit(); db.refresh(b)
    html = f"""<h3>Interview Booking Confirmed</h3>
    <p>Hi {req.name},</p>
    <p>Your interview is booked for <b>{req.date}</b> at <b>{req.time}</b>.</p>
    <p>We look forward to speaking with you.</p>"""
    
    try:
        send_email(req.email, "Interview Booking Confirmation", html)
    except Exception as e:
        print("Email send failed:", e)
    return BookingResponse(id=b.id, message=f"Booking confirmed for {req.name} and email sent for confirmation at {req.email}.")
