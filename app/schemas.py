# Pydantic schemas define the shape of data going in and out of the API.
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserSignup(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"



class ClassCreate(BaseModel):
    name: str = Field(..., min_length=1)
    dateTime: datetime  # any timezone accepted; normalized to IST internally
    instructor: str = Field(..., min_length=1)
    availableSlots: int = Field(..., ge=0)


class ClassOut(BaseModel):
    id: int
    name: str
    dateTime: datetime
    instructor: str
    availableSlots: int

    model_config = ConfigDict(from_attributes=True)


class BookingCreate(BaseModel):
    class_id: int
    client_name: str = Field(..., min_length=1)
    client_email: EmailStr


class BookingOut(BaseModel):
    id: int
    class_id: int
    class_name: str
    client_name: str
    client_email: str
    dateTime: datetime

    model_config = ConfigDict(from_attributes=True)
