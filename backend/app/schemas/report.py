from pydantic import BaseModel

class ReportCreate(BaseModel):
    title: str
    body: str | None = None

class ReportOut(BaseModel):
    id: int
    title: str
    body: str | None
    class Config:
        from_attributes = True
