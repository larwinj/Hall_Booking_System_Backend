from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Literal
from app.models.enums import UserRole
from app.schemas.venue import VenueCreate

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Valid email address of the user")
    role: UserRole = Field(..., description="Role assigned to the user (e.g., admin, moderator, customer)")

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="Valid email address for user registration")
    password: str = Field(
        ...,
        min_length=8,
        max_length=64,
        description="Password must be 8-64 chars long and include both letters and numbers",
    )

    @field_validator("password")
    def strong_password(cls, v: str) -> str:
        """Ensure password contains both letters and numbers and is not too weak."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if "password" in v.lower():
            raise ValueError("Password cannot contain the word 'password'")

        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")

        if not any(c in "!@#$%^&*()-_=+[]{}|;:',.<>?/`~" for c in v):
            raise ValueError("Password must contain at least one special character")

        return v

class UserAdminCreate(UserCreate):
    role: UserRole = Field(..., description="Role assigned to the user (Admin/Moderator)")
    assigned_venue_id: int | None = Field(
        None,
        ge=1,
        description="Optional venue ID assigned to a moderator (must be positive if provided)",
    )

class UserOut(BaseModel):
    id: int = Field(..., ge=1, description="Unique ID of the user")
    email: EmailStr = Field(..., description="User's email address")
    role: UserRole = Field(..., description="User's role in the system")
    is_active: bool = Field(..., description="Whether the user is active")
    assigned_venue_id: int | None = Field(
        None,
        ge=1,
        description="Venue ID assigned to moderator, if applicable",
    )

    class Config:
        from_attributes = True

class TokenPair(BaseModel):
    access_token: str = Field(..., min_length=10, description="JWT access token")
    refresh_token: str = Field(..., min_length=10, description="JWT refresh token")
    token_type: Literal["bearer"] = Field(
        default="bearer", description="Token type (always 'bearer')"
    )

class ModeratorRegistration(BaseModel):
    user: UserCreate = Field(..., description="User details for moderator registration")
    venue: VenueCreate = Field(..., description="Venue details linked to this moderator")

class LoginRequest(BaseModel):
    username: EmailStr = Field(..., description="User's email address used for login")
    password: str = Field(
        ...,
        min_length=8,
        max_length=64,
        description="User's password (min 8 characters, must include letters and numbers)",
    )
