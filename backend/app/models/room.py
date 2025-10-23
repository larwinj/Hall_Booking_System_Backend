from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Float, ARRAY, Text
from app.db.base_class import Base

class Room(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    venue_id: Mapped[int] = mapped_column(ForeignKey("venue.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    rate_per_hour: Mapped[float] = mapped_column(Float, nullable=False)
    amenities: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    venue = relationship("Venue", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room", cascade="all, delete-orphan")