# app/models/room.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Float, ARRAY, Text, JSON, Boolean
from app.db.base_class import Base

class Room(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    venue_id: Mapped[int] = mapped_column(ForeignKey("venue.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    rate_per_hour: Mapped[float] = mapped_column(Float, nullable=False)

    type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    amenities: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # New field for storing room images as JSON (list of base64 strings)
    room_images: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    venue = relationship("Venue", back_populates="rooms")
    addons = relationship("Addon", back_populates="room", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="room", cascade="all, delete-orphan")

    @property
    def venue_name(self):
        return self.venue.name if self.venue else None