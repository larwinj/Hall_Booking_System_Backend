from pydantic import BaseModel

class VenueBase(BaseModel):
    name: str
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    description: str | None = None

class VenueCreate(VenueBase):
    pass

class VenueUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    description: str | None = None

class VenueOut(VenueBase):
    id: int
    class Config:
        from_attributes = True
        
    