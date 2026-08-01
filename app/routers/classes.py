
# Creating and listing fitness classes.

from fastapi import APIRouter, Depends
from sqlalchemy import asc
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db
from ..timezone_utils import to_ist_naive, attach_ist, now_ist_naive

router = APIRouter(tags=["Classes"])


@router.post("/classes", response_model=schemas.ClassOut, status_code=201)
def create_class(
    payload: schemas.ClassCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    new_class = models.FitnessClass(
        name=payload.name,
        date_time_ist=to_ist_naive(payload.dateTime),
        instructor=payload.instructor,
        available_slots=payload.availableSlots,
        created_by=current_user.id,
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)

    return schemas.ClassOut(
        id=new_class.id,
        name=new_class.name,
        dateTime=attach_ist(new_class.date_time_ist),
        instructor=new_class.instructor,
        availableSlots=new_class.available_slots,
    )


@router.get("/classes", response_model=list[schemas.ClassOut])
def list_classes(db: Session = Depends(get_db)):
    """
    Public endpoint — no login required, so people can browse before
    signing up. Only shows classes that haven't happened yet, soonest first.
    """
    classes = (
        db.query(models.FitnessClass)
        .filter(models.FitnessClass.date_time_ist >= now_ist_naive())
        .order_by(asc(models.FitnessClass.date_time_ist))
        .all()
    )
    return [
        schemas.ClassOut(
            id=c.id,
            name=c.name,
            dateTime=attach_ist(c.date_time_ist),
            instructor=c.instructor,
            availableSlots=c.available_slots,
        )
        for c in classes
    ]
