from pydantic import BaseModel, Field, field_validator
from typing import Any, List

class Message(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="A human-readable message about the operation outcome.",
        examples=["Operation completed successfully", "Item deleted"]
    )

    @field_validator("message")
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("Message cannot be empty or only whitespace.")
        return v

class ErrorResponse(BaseModel):
    success: bool = Field(
        default=False,
        description="Indicates failure; always False for error responses."
    )
    error: dict = Field(
        ...,
        description="Detailed error information (code and message).",
        examples=[{"code": "bad_request", "message": "Invalid input"}]
    )

    @field_validator("error")
    def validate_error_structure(cls, v):
        if not isinstance(v, dict):
            raise ValueError("Error must be a dictionary.")
        if "code" not in v or "message" not in v:
            raise ValueError("Error dict must include 'code' and 'message' keys.")
        return v

class Paginated(BaseModel):
    total: int = Field(
        ...,
        ge=0,
        description="Total number of records available for pagination.",
        examples=[150]
    )
    items: List[Any] = Field(
        default_factory=list,
        description="A list of paginated result items."
    )

    @field_validator("total")
    def validate_total(cls, v):
        if v < 0:
            raise ValueError("Total count cannot be negative.")
        return v
