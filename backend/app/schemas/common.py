from pydantic import BaseModel, Field
from datetime import datetime

class Message(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    success: bool = False
    error: dict = Field(..., examples=[{"code": "bad_request", "message": "Invalid input"}])

class Paginated(BaseModel):
    total: int
    items: list
