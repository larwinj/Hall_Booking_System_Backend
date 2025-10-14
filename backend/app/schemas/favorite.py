from pydantic import BaseModel

class FavoriteCreate(BaseModel):
    room_id: int

class FavoriteOut(BaseModel):
    id: int
    room_id: int
    class Config:
        from_attributes = True
