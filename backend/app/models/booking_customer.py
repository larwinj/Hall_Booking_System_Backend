# app/models/booking_customer.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey, String, Index
from app.db.base_class import Base

class BookingCustomer(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("booking.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(512), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)

    __table_args__ = (
        Index('uq_booking_user', "booking_id", "user_id", unique=True, postgresql_where="user_id IS NOT NULL"),
    )

    booking = relationship("Booking", back_populates="customers")