
# Booking a class, and viewing your own bookings.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db
from ..timezone_utils import attach_ist

router = APIRouter(tags=["Bookings"])


@router.post("/book", response_model=schemas.BookingOut, status_code=201)
def book_class(
    payload: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    fitness_class = (
        db.query(models.FitnessClass)
        .filter(models.FitnessClass.id == payload.class_id)
        .first()
    )

    if not fitness_class:
        raise HTTPException(status_code=404, detail="Class not found")

    if fitness_class.available_slots <= 0:
        raise HTTPException(status_code=400, detail="No slots available for this class")

   
    fitness_class.available_slots -= 1

    booking = models.Booking(
        class_id=fitness_class.id,
        user_id=current_user.id,
        client_name=payload.client_name,
        client_email=payload.client_email,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    return schemas.BookingOut(
        id=booking.id,
        class_id=fitness_class.id,
        class_name=fitness_class.name,
        client_name=booking.client_name,
        client_email=booking.client_email,
        dateTime=attach_ist(fitness_class.date_time_ist),
    )


@router.get("/bookings", response_model=list[schemas.BookingOut])
def my_bookings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    bookings = (
        db.query(models.Booking)
        .filter(models.Booking.user_id == current_user.id)
        .all()
    )

    return [
        schemas.BookingOut(
            id=b.id,
            class_id=b.class_id,
            class_name=b.fitness_class.name,
            client_name=b.client_name,
            client_email=b.client_email,
            dateTime=attach_ist(b.fitness_class.date_time_ist),
        )
        for b in bookings
    ]
