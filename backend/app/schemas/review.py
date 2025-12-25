from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class ReviewCreate(BaseModel):
    booking_id: int = Field(..., ge=1, description="ID of the booking being reviewed")
    room_id: int = Field(..., ge=1, description="ID of the room being reviewed")
    rating: float = Field(
        ...,
        ge=0,
        le=5,
        description="Rating for the room (0 to 5 stars)"
    )
    comment: str | None = Field(
        None,
        min_length=3,
        max_length=500,
        description="Optional comment about the room experience (3-500 characters)"
    )

    @field_validator("comment")
    def clean_comment(cls, v):
        if v and not v.strip():
            raise ValueError("Comment cannot be blank or whitespace only")
        return v

class ReviewUpdate(BaseModel):
    rating: float = Field(
        ...,
        ge=0,
        le=5,
        description="Updated rating for the room (0 to 5 stars)"
    )
    comment: str | None = Field(
        None,
        max_length=500,
        description="Updated comment about the room experience"
    )
    
class ReviewOut(BaseModel):
    id: int = Field(..., ge=1, description="Unique ID of the review")
    booking_id: int = Field(..., ge=1, description="ID of the booking being reviewed")
    room_id: int = Field(..., ge=1, description="ID of the room being reviewed")
    user_id: int = Field(..., ge=1, description="ID of the user who wrote the review")
    rating: float = Field(..., ge=0, le=5, description="Star rating (0–5)")
    comment: str | None = Field(None, description="User's review comment, if any")
    created_at: datetime | None = Field(None, description="Review creation timestamp")
    updated_at: datetime | None = Field(None, description="Review update timestamp")

    class Config:
        from_attributes = True
