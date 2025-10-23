from pydantic import BaseModel, EmailStr
from app.models.enums import UserRole
from app.schemas.venue import VenueCreate

class UserBase(BaseModel):
    email: EmailStr
    role: UserRole

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserAdminCreate(UserCreate):
    role: UserRole
    assigned_venue_id: int | None = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    is_active: bool
    assigned_venue_id: int | None = None

    class Config:
        from_attributes = True

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class ModeratorRegistration(BaseModel):
    user: UserCreate
    venue: VenueCreate