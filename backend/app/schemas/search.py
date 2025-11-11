from pydantic import BaseModel
from typing import List
from datetime import date, datetime, timezone


class UnavailableSlot(BaseModel):
    start_time: str
    end_time: str
    status: str

class RoomUnavailableResponse(BaseModel):
    room_id: int
    date: date
    unavailable_slots: List[UnavailableSlot]

class AvailableSlot(BaseModel):
    start_time: str
    end_time: str

class RoomAvailableResponse(BaseModel):
    room_id: int
    date: date
    available_slots: List[AvailableSlot]