from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List

class BookingAddonItem(BaseModel):
    addon_id: int
    quantity: int

class BookingCreate(BaseModel):
    room_id: int
    start_time: datetime
    end_time: datetime
    customer_ids: List[int] = []
    addons: List[BookingAddonItem] = []

    @field_validator("end_time")
    @classmethod
    def end_after_start(cls, v, info):
        start_time = info.data.get("start_time")
        if start_time and v <= start_time:
            raise ValueError("end_time must be after start_time")
        return v

class BookingOut(BaseModel):
    id: int
    room_id: int
    start_time: datetime
    end_time: datetime
    status: str
    total_cost: float
    rescheduled: bool

    class Config:
        from_attributes = True

class BookingReschedule(BaseModel):
    start_time: datetime
    end_time: datetime

class BookingCancel(BaseModel):
    reason: str | None = None
