from pydantic import BaseModel
from app.models.enums import QueryStatus

class QueryCreate(BaseModel):
    subject: str
    message: str

class QueryUpdate(BaseModel):
    status: QueryStatus

class QueryOut(BaseModel):
    id: int
    subject: str
    message: str
    status: QueryStatus
    class Config:
        from_attributes = True
