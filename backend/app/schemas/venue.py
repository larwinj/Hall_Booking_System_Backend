from pydantic import BaseModel, Field


class VenueBase(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Name of the venue (3–100 characters)",
    )
    address: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Street address of the venue",
    )
    city: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="City where the venue is located",
    )
    state: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="State or province of the venue",
    )
    country: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Country where the venue is located",
    )
    postal_code: str = Field(
        ...,
        pattern=r"^[A-Za-z0-9\s-]{4,10}$",
        description="Postal or ZIP code (4–10 alphanumeric characters)",
    )
    description: str | None = Field(
        None,
        max_length=500,
        description="Optional description of the venue (up to 500 characters)",
    )


class VenueCreate(VenueBase):
    """Schema for creating a new venue"""
    pass


class VenueUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=100, description="Updated name of the venue")
    address: str | None = Field(None, min_length=5, max_length=255, description="Updated address")
    city: str | None = Field(None, min_length=2, max_length=100, description="Updated city")
    state: str | None = Field(None, min_length=2, max_length=100, description="Updated state or province")
    country: str | None = Field(None, min_length=2, max_length=100, description="Updated country")
    postal_code: str | None = Field(None, pattern=r"^[A-Za-z0-9\s-]{4,10}$", description="Updated postal code")
    description: str | None = Field(None, max_length=500, description="Updated venue description")


class VenueOut(VenueBase):
    id: int = Field(..., ge=1, description="Unique identifier for the venue")

    class Config:
        from_attributes = True
