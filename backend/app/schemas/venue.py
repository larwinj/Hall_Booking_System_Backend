from pydantic import BaseModel, Field
from datetime import date
from typing import List, Dict, Any

class VenueBase(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Name of the venue (3–100 characters)",
    )
    address: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Street address of the venue",
    )
    city: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="City where the venue is located",
    )
    state: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="State or province of the venue",
    )
    country: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Country where the venue is located",
    )
    postal_code: str = Field(
        ...,
        pattern=r"^[A-Za-z0-9\s-]{4,10}$",
        description="Postal or ZIP code (4–10 alphanumeric characters)",
    )
    description: str | None = Field(
        None,
        max_length=500,
        description="Optional description of the venue (up to 500 characters)",
    )


class VenueCreate(VenueBase):
    """Schema for creating a new venue"""
    pass


class VenueUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=100, description="Updated name of the venue")
    address: str | None = Field(None, min_length=5, max_length=255, description="Updated address")
    city: str | None = Field(None, min_length=2, max_length=100, description="Updated city")
    state: str | None = Field(None, min_length=2, max_length=100, description="Updated state or province")
    country: str | None = Field(None, min_length=2, max_length=100, description="Updated country")
    postal_code: str | None = Field(None, pattern=r"^[A-Za-z0-9\s-]{4,10}$", description="Updated postal code")
    description: str | None = Field(None, max_length=500, description="Updated venue description")


class VenueOut(VenueBase):
    id: int = Field(..., ge=1, description="Unique identifier for the venue")

    class Config:
        from_attributes = True


class VenueRangeReport(BaseModel):
    venue_id: int = Field(..., description="Venue ID")
    venue_name: str = Field(..., description="Venue name")
    start_date: date = Field(..., description="Report start date")
    end_date: date = Field(..., description="Report end date")
    total_bookings: int = Field(..., description="Total number of bookings")
    total_revenue: float = Field(..., description="Total revenue generated")
    confirmed_bookings: int = Field(..., description="Number of confirmed bookings")
    cancelled_bookings: int = Field(..., description="Number of cancelled bookings")
    pending_bookings: int = Field(..., description="Number of pending bookings")
    rescheduled_bookings: int = Field(..., description="Number of rescheduled bookings")
    average_booking_value: float = Field(..., description="Average booking value")
    
    # Room-wise breakdown
    room_breakdown: List[Dict[str, Any]] = Field(..., description="Booking breakdown by room")
    
    # Daily trend
    daily_trend: List[Dict[str, Any]] = Field(..., description="Daily booking trend")
    
    # Booking status distribution
    status_distribution: Dict[str, int] = Field(..., description="Booking status count")
    
    # Peak performance hours
    peak_hours: List[Dict[str, Any]] = Field(..., description="Most popular booking hours")

    class Config:
        from_attributes = True
        
class LocationAnalyticsReport(BaseModel):
    city: str = Field(..., description="City name")
    total_venues: int = Field(..., description="Total number of venues in the city")
    total_bookings: int = Field(..., description="Total number of bookings")
    total_revenue: float = Field(..., description="Total revenue generated")
    average_booking_value: float = Field(..., description="Average booking value across all venues")
    overall_occupancy_rate: float = Field(..., description="Overall occupancy rate percentage")
    
    # Venue performance in the city
    venue_performance: List[Dict[str, Any]] = Field(..., description="Performance by venue")
    
    # Room type analysis
    room_type_analysis: List[Dict[str, Any]] = Field(..., description="Analysis by room types")
    
    # Monthly trend for the city
    monthly_trend: List[Dict[str, Any]] = Field(..., description="Monthly booking trend")
    
    # Customer demographics
    total_customers: int = Field(..., description="Total number of unique customers")
    customer_cities: List[Dict[str, Any]] = Field(..., description="Customer distribution by city")
    
    # Peak seasons
    peak_seasons: List[Dict[str, Any]] = Field(..., description="Peak booking seasons")
    
    # Revenue distribution
    revenue_distribution: Dict[str, float] = Field(..., description="Revenue distribution across venues")

    class Config:
        from_attributes = True