# app/schemas/room.py
from pydantic import BaseModel, Field, field_validator
from typing import List
from app.schemas.addon import AddonBase
from fastapi import UploadFile

class RoomAddonCreate(AddonBase):
    """Schema for creating room addons (inherits AddonBase)."""
    pass

class RoomBase(BaseModel):
    venue_id: int = Field(..., ge=1, description="ID of the venue this room belongs to")
    name: str = Field(..., min_length=3, max_length=100, description="Name of the room")
    capacity: int = Field(..., ge=1, le=1000, description="Seating capacity of the room (1-1000)")
    rate_per_hour: float = Field(..., gt=0, description="Hourly rate for booking this room (must be positive)")
    type: str | None = Field(
        default="standard",
        example="conference",
        description="Type of the room (e.g., conference, meeting, banquet)"
    )
    amenities: List[str] = Field(
        default_factory=list,
        description="List of amenities available in the room (e.g., AC, Projector, Whiteboard)"
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Optional detailed description of the room"
    )
    status: bool = Field(
        default=True,
        description="Room availability status (True=Available for booking, False=Not Available)"
    )

    @field_validator("amenities")
    def no_empty_amenities(cls, v: List[str]) -> List[str]:
        """Ensure no empty amenities and clean up whitespace."""
        cleaned = [item.strip() for item in v if item.strip()]
        if len(cleaned) != len(v):
            raise ValueError("Amenities cannot contain empty or blank entries")
        return cleaned

class RoomCreate(BaseModel):
    venue_id: int = Field(..., ge=1, description="ID of the venue this room belongs to")
    name: str = Field(..., min_length=3, max_length=100, description="Name of the room")
    capacity: int = Field(..., ge=1, le=1000, description="Seating capacity of the room (1-1000)")
    rate_per_hour: float = Field(..., gt=0, description="Hourly rate for booking this room (must be positive)")
    type: str | None = Field(
        default="standard",
        example="conference",
        description="Type of the room (e.g., conference, meeting, banquet)"
    )
    amenities: List[str] = Field(
        default_factory=list,
        description="List of amenities available in the room (e.g., AC, Projector, Whiteboard)"
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Optional detailed description of the room"
    )
    addons: List[RoomAddonCreate] = Field(
        default_factory=list,
        description="List of addons available for this room"
    )
    status: bool = Field(default=True, description="Room availability status (True=Available, False=Not Available).")

    @field_validator("amenities")
    def no_empty_amenities(cls, v: List[str]) -> List[str]:
        """Ensure no empty amenities and clean up whitespace."""
        cleaned = [item.strip() for item in v if item.strip()]
        if len(cleaned) != len(v):
            raise ValueError("Amenities cannot contain empty or blank entries")
        return cleaned

class RoomUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=100, description="Updated name of the room")
    capacity: int | None = Field(None, ge=1, le=1000, description="Updated capacity of the room")
    rate_per_hour: float | None = Field(None, gt=0, description="Updated rate per hour (must be positive)")
    type: str | None = Field(None, description="Updated room type")
    amenities: List[str] | None = Field(None, description="Updated amenities list")
    description: str | None = Field(None, max_length=500, description="Updated room description")
    addons: List[RoomAddonCreate] | None = Field(None, description="Updated list of addons")
    status: bool | None = Field(None, description="Room availability status (True=Available, False=Not Available).")

    @field_validator("amenities")
    def validate_amenities(cls, v):
        if v is not None:
            cleaned = [item.strip() for item in v if item.strip()]
            if len(cleaned) != len(v):
                raise ValueError("Amenities cannot contain empty or blank entries")
        return v

class RoomOut(RoomBase):
    id: int = Field(..., ge=1, description="Unique ID of the room")
    venue_name: str | None = Field(None, description="Name of the venue")

    class Config:
        from_attributes = True