"""
Basic smoke tests covering the main flow: signup -> login -> create class
-> list classes -> book -> prevent overbooking -> view bookings.

Run with:
    pytest -v


"""
import os

os.environ.setdefault("JWT_SECRET_KEY", "test-secret")

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_signup_and_login():
    email = "test_user@example.com"
    signup_response = client.post(
        "/signup", json={"name": "Test", "email": email, "password": "test1234"}
    )
    # 201 on first run, 400 ("already registered") on any re-run - both fine.
    assert signup_response.status_code in (201, 400)

    login_response = client.post("/login", json={"email": email, "password": "test1234"})
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_login_wrong_password_fails():
    email = "test_user@example.com"
    client.post("/signup", json={"name": "Test", "email": email, "password": "test1234"})
    response = client.post("/login", json={"email": email, "password": "wrong-password"})
    assert response.status_code == 401


def test_full_booking_flow_and_overbooking_guard():
    email = "test_user2@example.com"
    client.post("/signup", json={"name": "Test2", "email": email, "password": "test1234"})
    login = client.post("/login", json={"email": email, "password": "test1234"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    class_payload = {
        "name": "Test Yoga",
        "dateTime": "2030-01-01T10:00:00Z",
        "instructor": "Test Instructor",
        "availableSlots": 1,
    }
    create_response = client.post("/classes", json=class_payload, headers=headers)
    assert create_response.status_code == 201
    class_id = create_response.json()["id"]

    list_response = client.get("/classes")
    assert list_response.status_code == 200
    assert any(c["id"] == class_id for c in list_response.json())

    booking_payload = {
        "class_id": class_id,
        "client_name": "Alice",
        "client_email": "alice@example.com",
    }
    first_booking = client.post("/book", json=booking_payload, headers=headers)
    assert first_booking.status_code == 201

    # Only 1 slot existed - this second attempt must be rejected.
    second_booking = client.post("/book", json=booking_payload, headers=headers)
    assert second_booking.status_code == 400

    my_bookings = client.get("/bookings", headers=headers)
    assert my_bookings.status_code == 200
    assert len(my_bookings.json()) >= 1


def test_protected_routes_require_auth():
    response = client.post(
        "/book", json={"class_id": 1, "client_name": "X", "client_email": "x@example.com"}
    )
    assert response.status_code == 401

    response = client.get("/bookings")
    assert response.status_code == 401

    response = client.post(
        "/classes",
        json={
            "name": "X",
            "dateTime": "2030-01-01T10:00:00Z",
            "instructor": "X",
            "availableSlots": 1,
        },
    )
    assert response.status_code == 401
