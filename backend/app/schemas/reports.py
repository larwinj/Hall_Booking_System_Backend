from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import date

class UserBookingSummary(BaseModel):
    user_id: int | None
    first_name: str
    last_name: str
    phone: str
    total_bookings: int
    total_spent: float
    bookings: List[Dict[str, Any]]  # {booking_id, date, duration, cost, addons}

class RoomReport(BaseModel):
    room_id: int
    room_name: str
    room_type: str
    total_bookings: int
    total_revenue: float
    avg_duration_hours: float
    users: List[UserBookingSummary]

class VenueMonthlyReport(BaseModel):
    venue_id: int
    venue_name: str
    month_year: str
    total_bookings: int
    total_revenue: float
    rooms: List[RoomReport]

class ReportRequest(BaseModel):
    month_year: str  # e.g., "2025-10"