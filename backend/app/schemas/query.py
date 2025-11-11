from pydantic import BaseModel, Field, field_validator
from app.models.enums import QueryStatus

class QueryCreate(BaseModel):
    subject: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Short subject line describing the query (3-100 characters)"
    )
    message: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Detailed message body of the query (10-2000 characters)"
    )

    @field_validator("subject")
    def validate_subject(cls, v):
        if not v.strip():
            raise ValueError("Subject cannot be empty or only whitespace")
        return v

    @field_validator("message")
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("Message cannot be empty or only whitespace")
        return v

class QueryUpdate(BaseModel):
    status: QueryStatus = Field(..., description="Updated status of the query")


class QueryOut(BaseModel):
    id: int = Field(..., ge=1, description="Unique identifier for the query")
    subject: str = Field(..., description="Query subject line")
    message: str = Field(..., description="Detailed query message")
    status: QueryStatus = Field(..., description="Current status of the query")

    class Config:
        from_attributes = True