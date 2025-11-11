from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, DateTime
from datetime import datetime
from app.db.base_class import Base

class ReportCache(Base):
    __tablename__ = "report_cache"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    venue_id: Mapped[int] = mapped_column(ForeignKey("venue.id", ondelete="CASCADE"), index=True)
    month_year: Mapped[str] = mapped_column(String(7), index=True)  # e.g., "2025-10"
    mongo_doc_id: Mapped[str] = mapped_column(String(24), nullable=False)  # ObjectId as string
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    venue = relationship("Venue", back_populates="report_caches")