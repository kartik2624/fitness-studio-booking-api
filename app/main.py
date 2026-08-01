from fastapi import FastAPI

from . import models
from .database import engine
from .routers import users, classes, bookings

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fitness Studio Booking API",
    description="A simple booking system for a fictional fitness studio.",
    version="1.0.0",
)

app.include_router(users.router)
app.include_router(classes.router)
app.include_router(bookings.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Fitness Studio Booking API is running"}
