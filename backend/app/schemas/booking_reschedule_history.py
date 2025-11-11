from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class BookingRescheduleHistoryBase(BaseModel):
    original_room_id: int = Field(..., ge=1, description="Original room ID before reschedule")
    original_start_time: datetime = Field(..., description="Original start time before reschedule")
    original_end_time: datetime = Field(..., description="Original end time before reschedule")
    original_total_cost: float = Field(..., ge=0, description="Original total cost before reschedule")
    new_room_id: int = Field(..., ge=1, description="New room ID after reschedule")
    new_start_time: datetime = Field(..., description="New start time after reschedule")
    new_end_time: datetime = Field(..., description="New end time after reschedule")
    new_total_cost: float = Field(..., ge=0, description="New total cost after reschedule")
    price_difference: float = Field(..., description="Price difference (positive for additional payment, negative for refund)")
    refund_amount: float = Field(..., ge=0, description="Amount refunded to wallet")
    additional_amount: float = Field(..., ge=0, description="Additional amount required")
    reschedule_reason: Optional[str] = Field(None, description="Reason for reschedule")

class BookingRescheduleHistoryOut(BookingRescheduleHistoryBase):
    id: int = Field(..., ge=1, description="Unique ID of the reschedule history record")
    booking_id: int = Field(..., ge=1, description="ID of the booking that was rescheduled")
    created_at: datetime = Field(..., description="When the reschedule was recorded")

    class Config:
        from_attributes = True

class BookingWithRescheduleHistory(BaseModel):
    booking: dict  # This will be the BookingOut schema
    reschedule_history: list[BookingRescheduleHistoryOut] = Field(default_factory=list, description="History of reschedules for this booking")