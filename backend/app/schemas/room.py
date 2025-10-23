from pydantic import BaseModel, Field
from typing import List
from app.schemas.addon import AddonBase

class RoomAddonCreate(AddonBase):
    pass

class RoomBase(BaseModel):
    venue_id: int
    name: str
    capacity: int
    rate_per_hour: float
    amenities: List[str] = Field(default_factory=list)
    description: str | None = None

class RoomCreate(RoomBase):
    addons: List[RoomAddonCreate] = []

class RoomUpdate(BaseModel):
    name: str | None = None
    capacity: int | None = None
    rate_per_hour: float | None = None
    amenities: List[str] | None = None
    description: str | None = None

class RoomOut(RoomBase):
    id: int
    class Config:
        from_attributes = True