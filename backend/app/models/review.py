from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, ForeignKey, Text, Float, DateTime, UniqueConstraint
from datetime import datetime, timezone
from app.db.base_class import Base

class Review(Base):
    __table_args__ = (
        UniqueConstraint('booking_id', name='uq_review_booking'),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("room.id", ondelete="CASCADE"), index=True)
    booking_id: Mapped[int | None] = mapped_column(ForeignKey("booking.id", ondelete="CASCADE"), index=True, unique=True, nullable=True)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, onupdate=lambda: datetime.now(timezone.utc))

