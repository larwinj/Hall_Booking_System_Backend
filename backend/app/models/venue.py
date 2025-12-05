from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text
from app.db.base_class import Base
from app.models.report_cache import ReportCache

class Venue(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    address: Mapped[str] = mapped_column(String(512), nullable=False)
    city: Mapped[str] = mapped_column(String(128), index=True)
    state: Mapped[str] = mapped_column(String(128))
    country: Mapped[str] = mapped_column(String(128))
    postal_code: Mapped[str] = mapped_column(String(32))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    rooms = relationship("Room", back_populates="venue", cascade="all, delete-orphan")
    moderators = relationship("User", back_populates="assigned_venue")
    addons = relationship("Addon", back_populates="venue", cascade="all, delete-orphan")
    report_caches = relationship("ReportCache", back_populates="venue", cascade="all, delete-orphan")