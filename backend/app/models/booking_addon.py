from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey, Float
from app.db.base_class import Base

class BookingAddon(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("booking.id", ondelete="CASCADE"), index=True)
    addon_id: Mapped[int] = mapped_column(ForeignKey("addon.id", ondelete="CASCADE"), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    booking = relationship("Booking", back_populates="addons")
    addon = relationship("Addon", back_populates="booking_addons")
