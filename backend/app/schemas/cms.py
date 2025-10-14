from pydantic import BaseModel, Field
from typing import Any, Dict

class CMSBase(BaseModel):
    slug: str
    title: str
    html_content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    attachments: list[str] = Field(default_factory=list)
    published: bool = False

class CMSUpdate(BaseModel):
    title: str | None = None
    html_content: str | None = None
    metadata: Dict[str, Any] | None = None
    attachments: list[str] | None = None
    published: bool | None = None
