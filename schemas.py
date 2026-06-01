from pydantic import EmailStr, Field, BaseModel
from typing import Optional
from datetime import datetime


# Auth
class SignupRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=15)
    full_name: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=3)



class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# User
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)


# Booking


class CreateBookingRequest(BaseModel):
    movie_id: int
    movie_title: str
    movie_poster: Optional[str] = None
    cinema_name: str
    show_date: str  # e.g. '2024-12-25'
    show_time: str  # eg. 19:30
    seats: int = Field(ge=1, le=10)
    total_price: str  # e.g GHC 45.00


class BookingResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    movie_title: str
    movie_poster: Optional[str] = None
    cinema_name: str
    show_date: str  # e.g. '2024-12-25'
    show_time: str  # eg. 19:30
    seats: int
    total_price: str  # e.g GHC 45.00
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Generic


class MessageResponse(BaseModel):
    message: str


class TokenResponse(BaseModel):
    message: str
    user: UserResponse
