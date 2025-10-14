from pydantic import BaseModel

class AddonBase(BaseModel):
    name: str
    description: str | None = None
    price: float

class AddonCreate(AddonBase):
    pass

class AddonUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None

class AddonOut(AddonBase):
    id: int
    class Config:
        from_attributes = True
