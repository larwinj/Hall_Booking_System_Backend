from pydantic import BaseModel

class ReviewCreate(BaseModel):
    room_id: int
    rating: float
    comment: str | None = None

class ReviewOut(BaseModel):
    id: int
    room_id: int
    rating: float
    comment: str | None
    class Config:
        from_attributes = True
