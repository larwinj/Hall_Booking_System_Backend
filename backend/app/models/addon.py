from sqlalchemy import String, Integer, Float, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class Addon(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    venue_id: Mapped[int] = mapped_column(ForeignKey("venue.id", ondelete="CASCADE"), index=True, nullable=False)
    room_id: Mapped[int | None] = mapped_column(ForeignKey("room.id", ondelete="CASCADE"), index=True, nullable=True)

    # NOTE: removed unique=True
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    venue = relationship("Venue", back_populates="addons")
    room = relationship("Room", back_populates="addons")
    booking_addons = relationship("BookingAddon", back_populates="addon", cascade="all, delete-orphan")

    # Optional: table-level constraints (choose one approach below)
    __table_args__ = (
        # Approach A (recommended): prevent duplicate names *within the same room*,
        # but allow the same name across different rooms. Null room_id (venue-level addons)
        # are not covered by this index.
        # UniqueConstraint('room_id', 'name', name='uix_room_addon_name'),
    )
