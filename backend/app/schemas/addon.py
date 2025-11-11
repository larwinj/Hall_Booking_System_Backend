from pydantic import BaseModel, Field, field_validator

class AddonBase(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Name of the addon (2-100 characters).",
        examples=["Projector", "Sound System"]
    )
    description: str | None = Field(
        default=None,
        max_length=300,
        description="Optional detailed description of the addon."
    )
    price: float = Field(
        ...,
        gt=0,
        description="Price of the addon (must be a positive value).",
        examples=[500.0]
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Addon name cannot be empty or only whitespace.")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("Addon price must be greater than zero.")
        return v

class AddonCreate(AddonBase):
    venue_id: int = Field(
        ...,
        gt=0,
        description="ID of the venue this addon belongs to."
    )
    room_id: int | None = Field(
        default=None,
        gt=0,
        description="Optional ID of the specific room if the addon is room-specific."
    )

    @field_validator("venue_id", "room_id")
    @classmethod
    def validate_ids(cls, v, info):
        if v is not None and v <= 0:
            raise ValueError(f"{info.field_name} must be a positive integer.")
        return v

class AddonUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Updated addon name."
    )
    description: str | None = Field(
        default=None,
        max_length=300,
        description="Updated addon description."
    )
    price: float | None = Field(
        default=None,
        gt=0,
        description="Updated addon price."
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v and not v.strip():
            raise ValueError("Addon name cannot be only whitespace.")
        return v


class AddonOut(AddonBase):
    id: int = Field(..., ge=1, description="Unique identifier of the addon.")
    venue_id: int = Field(..., ge=1, description="ID of the venue this addon belongs to.")
    room_id: int | None = Field(default=None, ge=1, description="Room ID if addon is room-specific.")

    class Config:
        from_attributes = True