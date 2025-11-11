from pydantic import BaseModel, Field, field_validator

class ReportCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="Short descriptive title for the report (3-150 characters)"
    )
    body: str | None = Field(
        None,
        min_length=10,
        max_length=2000,
        description="Detailed body text of the report (optional, 10-2000 characters)"
    )

    @field_validator("title")
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v

    @field_validator("body")
    def validate_body(cls, v):
        if v and not v.strip():
            raise ValueError("Body cannot be blank or whitespace only")
        return v

class ReportOut(BaseModel):
    id: int = Field(..., ge=1, description="Unique identifier for the report")
    title: str = Field(..., description="Title of the report")
    body: str | None = Field(None, description="Detailed body of the report, if provided")

    class Config:
        from_attributes = True
