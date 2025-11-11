from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, JSON, Enum
from datetime import datetime, timezone
from app.db.base_class import Base
from app.models.enums import PublicationStatus

class Backup(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    backup_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[PublicationStatus] = mapped_column(Enum(PublicationStatus, name="backup_status_enum"), default=PublicationStatus.published, nullable=False)
    
    # vercel data fields
    vercel_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    vercel_pathname: Mapped[str | None] = mapped_column(String(500), nullable=True)
    vercel_filename: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))