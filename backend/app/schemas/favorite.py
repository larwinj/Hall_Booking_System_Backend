from pydantic import BaseModel, Field, field_validator

class FavoriteCreate(BaseModel):
    room_id: int = Field(
        ...,
        gt=0,
        description="ID of the room being marked as favorite (must be a positive integer)"
    )

    @field_validator("room_id")
    def validate_room_id(cls, v):
        if v <= 0:
            raise ValueError("room_id must be a positive integer")
        return v

class FavoriteOut(BaseModel):
    id: int = Field(..., ge=1, description="Unique identifier of the favorite record")
    room_id: int = Field(..., ge=1, description="ID of the favorited room")

    class Config:
        from_attributes = True
