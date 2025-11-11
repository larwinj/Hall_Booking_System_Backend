from pydantic import BaseModel, Field, field_validator

class ReviewCreate(BaseModel):
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
    
class ReviewOut(BaseModel):
    id: int = Field(..., ge=1, description="Unique ID of the review")
    room_id: int = Field(..., ge=1, description="ID of the room being reviewed")
    rating: float = Field(..., ge=0, le=5, description="Star rating (0–5)")
    comment: str | None = Field(None, description="User's review comment, if any")

    class Config:
        from_attributes = True
