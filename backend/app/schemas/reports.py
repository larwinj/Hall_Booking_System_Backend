from pydantic import BaseModel, Field
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


class VenueAnalyticsReport(BaseModel):
    venue_id: int = Field(..., description="Venue ID")
    venue_name: str = Field(..., description="Venue name")
    period_days: int = Field(..., description="Number of days in the report period")
    report_date_range: str = Field(..., description="Date range of the report")
    total_bookings: int = Field(..., description="Total number of bookings")
    total_revenue: float = Field(..., description="Total revenue generated")
    average_booking_value: float = Field(..., description="Average booking value")
    occupancy_rate: float = Field(..., description="Occupancy rate percentage")
    cancelled_bookings: int = Field(..., description="Number of cancelled bookings")
    rescheduled_bookings: int = Field(..., description="Number of rescheduled bookings")
    
    # Room performance
    room_performance: List[Dict[str, Any]] = Field(..., description="Performance by room")
    
    # Daily breakdown
    daily_breakdown: List[Dict[str, Any]] = Field(..., description="Daily booking and revenue data")
    
    # Customer statistics
    total_customers: int = Field(..., description="Total number of unique customers")
    repeat_customers: int = Field(..., description="Number of repeat customers")
    
    # Addon statistics
    addon_revenue: float = Field(..., description="Revenue from addons")
    popular_addons: List[Dict[str, Any]] = Field(..., description="Most popular addons")
    
    # Time slot analysis
    peak_hours: List[Dict[str, Any]] = Field(..., description="Peak booking hours")
    
    class Config:
        from_attributes = True