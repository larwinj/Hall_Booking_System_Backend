from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Enum, ForeignKey, Boolean
from app.db.base_class import Base
from app.models.enums import UserRole
from app.models.wallet import Wallet

class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role_enum"), default=UserRole.customer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    assigned_venue_id: Mapped[int | None] = mapped_column(ForeignKey("venue.id"), nullable=True)
    # token version for refresh invalidation
    token_version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    assigned_venue = relationship("Venue", back_populates="moderators", foreign_keys=[assigned_venue_id])
    wallet = relationship("Wallet", back_populates="user", uselist=False, cascade="all, delete-orphan")