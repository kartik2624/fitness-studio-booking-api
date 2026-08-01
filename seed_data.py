"""
Populates the database with a demo user and a few sample classes, so you
have something to test against instead of an empty database.

Usage (after installing requirements):
    python seed_data.py
"""
from datetime import datetime, timedelta, timezone

from app.database import SessionLocal, engine
from app import models
from app.auth import hash_password
from app.timezone_utils import to_ist_naive

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

# --- demo user (email: demo@example.com, password: password123) ---
demo_user = db.query(models.User).filter(models.User.email == "demo@example.com").first()
if not demo_user:
    demo_user = models.User(
        name="Demo User",
        email="demo@example.com",
        hashed_password=hash_password("password123"),
    )
    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)
    print("Created demo user -> demo@example.com / password123")
else:
    print("Demo user already exists, skipping.")

# --- sample classes, spread a few days into the future ---
now_utc = datetime.now(timezone.utc)
sample_classes = [
    {"name": "Yoga Flow", "instructor": "John Doe", "availableSlots": 20, "offset_days": 1},
    {"name": "HIIT Session", "instructor": "Jane Smith", "availableSlots": 10, "offset_days": 2},
    {"name": "Zumba Blast", "instructor": "Maria Garcia", "availableSlots": 15, "offset_days": 3},
]

for c in sample_classes:
    already_exists = (
        db.query(models.FitnessClass)
        .filter(models.FitnessClass.name == c["name"])
        .first()
    )
    if already_exists:
        print(f"Class '{c['name']}' already exists, skipping.")
        continue

    class_time_utc = now_utc + timedelta(days=c["offset_days"])
    new_class = models.FitnessClass(
        name=c["name"],
        date_time_ist=to_ist_naive(class_time_utc),
        instructor=c["instructor"],
        available_slots=c["availableSlots"],
        created_by=demo_user.id,
    )
    db.add(new_class)
    print(f"Added class: {c['name']}")

db.commit()
db.close()
print("\nSeeding done.")
