# app/schemas/booking.py
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import List, Optional

import datetime as dt

class CustomerCreate(BaseModel):
    user_id: int | None = Field(None, description="Optional ID of registered user")
    first_name: str = Field(..., min_length=1, max_length=100, description="Customer's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Customer's last name")
    address: str = Field(..., min_length=5, max_length=512, description="Customer's address")
    phone: str = Field(..., min_length=10, max_length=50, description="Customer's phone number")

class BookingAddonItem(BaseModel):
    addon_id: int = Field(
        ...,
        gt=0,
        description="Unique ID of the addon item being booked (must be positive)."
    )
    quantity: int = Field(
        ...,
        gt=0,
        description="Quantity of the addon requested (must be at least 1)."
    )

    @field_validator("addon_id", "quantity")
    @classmethod
    def validate_positive_values(cls, v, info):
        if v <= 0:
            raise ValueError(f"{info.field_name} must be a positive integer.")
        return v

def compute_datetime_from_date_and_time(date_val: dt.date, time_str: str, timezone_val: timezone = timezone.utc) -> datetime:
    # Handle both colon and dot separators
    time_str_normalized = time_str.replace('.', ':')
    time_val = datetime.strptime(time_str_normalized, '%H:%M').time()
    return datetime.combine(date_val, time_val, tzinfo=timezone_val)

class BookingCreate(BaseModel):
    room_id: int = Field(
        ...,
        gt=0,
        description="ID of the room being booked (must be positive)."
    )
    date: dt.date = Field(
        ...,
        description="Booking date (YYYY-MM-DD format)."
    )
    start_time: str = Field(
        ...,
        pattern=r'^\d{2}[.:]\d{2}$',
        description="Booking start time in 24-hour format (HH:MM or HH.MM)."
    )
    end_time: str = Field(
        ...,
        pattern=r'^\d{2}[.:]\d{2}$',
        description="Booking end time in 24-hour format (HH:MM or HH.MM)."
    )
    customers: List[CustomerCreate] = Field(
        default_factory=list,
        description="List of customer details associated with the booking."
    )
    addons: List[BookingAddonItem] = Field(
        default_factory=list,
        description="List of addon items included in the booking."
    )

    @field_validator("room_id")
    @classmethod
    def validate_room_id(cls, v):
        if v <= 0:
            raise ValueError("room_id must be a positive integer.")
        return v

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, v):
        try:
            # Normalize and parse to validate
            v_normalized = v.replace('.', ':')
            datetime.strptime(v_normalized, '%H:%M')
            return v
        except ValueError:
            raise ValueError("Time must be in HH:MM or HH.MM (24-hour) format.")

    @field_validator("customers")
    @classmethod
    def validate_customers(cls, v):
        if not v:
            raise ValueError("At least one customer is required.")
        return v

    def compute_start_datetime(self) -> datetime:
        return compute_datetime_from_date_and_time(self.date, self.start_time)

    def compute_end_datetime(self) -> datetime:
        end_datetime = compute_datetime_from_date_and_time(self.date, self.end_time)
        if end_datetime <= self.compute_start_datetime():
            raise ValueError("end_time must be after start_time.")
        return end_datetime

class BookingOut(BaseModel):
    id: int = Field(..., ge=1, description="Unique identifier of the booking.")
    room_id: int = Field(..., ge=1, description="ID of the room booked.")
    start_time: datetime = Field(..., description="Booking start time.")
    end_time: datetime = Field(..., description="Booking end time.")
    status: str = Field(..., description="Current status of the booking (e.g., confirmed, cancelled).")
    total_cost: float = Field(..., ge=0, description="Total cost of the booking (cannot be negative).")
    rescheduled: bool = Field(..., description="Indicates if the booking was rescheduled.")

    class Config:
        from_attributes = True

class BookingReschedule(BaseModel):
    date: dt.date = Field(..., description="New booking date (YYYY-MM-DD format).")
    start_time: str = Field(
        ...,
        pattern=r'^\d{2}[.:]\d{2}$',
        description="New start time in 24-hour format (HH:MM or HH.MM)."
    )
    end_time: str = Field(
        ...,
        pattern=r'^\d{2}[.:]\d{2}$',
        description="New end time in 24-hour format (HH:MM or HH.MM)."
    )
    new_room_id: Optional[int] = Field(
        None,
        gt=0,
        description="Optional new room ID within the same venue for rescheduling"
    )

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, v):
        try:
            # Normalize and parse to validate
            v_normalized = v.replace('.', ':')
            datetime.strptime(v_normalized, '%H:%M')
            return v
        except ValueError:
            raise ValueError("Time must be in HH:MM or HH.MM (24-hour) format.")

    def compute_start_datetime(self) -> datetime:
        start_t = datetime.strptime(self.start_time.replace('.', ':'), '%H:%M').time()
        full_start = datetime.combine(self.date, start_t, tzinfo=timezone.utc)
        return full_start

    def compute_end_datetime(self) -> datetime:
        end_t = datetime.strptime(self.end_time.replace('.', ':'), '%H:%M').time()
        full_end = datetime.combine(self.date, end_t, tzinfo=timezone.utc)
        if full_end <= self.compute_start_datetime():
            raise ValueError("end_time must be after start_time for rescheduling.")
        return full_end

# Add new schema for reschedule response
class RescheduleResponse(BaseModel):
    booking: BookingOut
    price_difference: float = Field(..., description="Positive if refund, negative if additional payment needed")
    refund_amount: float = Field(..., ge=0, description="Amount refunded to wallet (if any)")
    additional_amount: float = Field(..., ge=0, description="Additional amount needed (if any)")
    message: str = Field(..., description="Reschedule summary message")

    class Config:
        from_attributes = True

class BookingCancel(BaseModel):
    reason: str | None = Field(
        default=None,
        max_length=300,
        description="Optional reason for cancellation (max 300 characters)."
    )

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v):
        if v and not v.strip():
            raise ValueError("Cancellation reason cannot be only whitespace.")
        return v