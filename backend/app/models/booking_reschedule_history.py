from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey, DateTime, Float, Text
from datetime import datetime, timezone
from app.db.base_class import Base

class BookingRescheduleHistory(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("booking.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # Original booking details (before reschedule)
    original_room_id: Mapped[int] = mapped_column(ForeignKey("room.id"), nullable=False)
    original_start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    original_end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    original_total_cost: Mapped[float] = mapped_column(Float, nullable=False)
    
    # New booking details (after reschedule)
    new_room_id: Mapped[int] = mapped_column(ForeignKey("room.id"), nullable=False)
    new_start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    new_end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    new_total_cost: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Financial details
    price_difference: Mapped[float] = mapped_column(Float, nullable=False)  # Positive if additional payment, negative if refund
    refund_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    additional_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    # Metadata
    reschedule_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    booking = relationship("Booking", back_populates="reschedule_history")
    original_room = relationship("Room", foreign_keys=[original_room_id])
    new_room = relationship("Room", foreign_keys=[new_room_id])