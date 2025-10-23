from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from app.db.base_class import Base

class BookingCustomer(Base):
    __table_args__ = (
        UniqueConstraint("booking_id", "user_id", name="uq_booking_user"),
    )
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("booking.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)

    booking = relationship("Booking", back_populates="customers")