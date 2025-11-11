from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, Optional
from app.models.enums import PublicationStatus

class BackupBase(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Name for the backup (3-255 characters)"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional description of the backup"
    )

class BackupCreate(BackupBase):
    pass

class BackupOut(BackupBase):
    id: int = Field(..., ge=1, description="Unique ID of the backup")
    backup_data: Dict[str, Any] = Field(..., description="The actual backup data in JSON format")
    status: PublicationStatus = Field(..., description="Status of the backup")
    
    # Add Vercel fields
    vercel_url: Optional[str] = Field(None, description="Vercel Blob storage URL")
    vercel_pathname: Optional[str] = Field(None, description="Vercel Blob storage pathname")
    vercel_filename: Optional[str] = Field(None, description="Vercel Blob storage filename")
    
    created_at: datetime = Field(..., description="When the backup was created")

    class Config:
        from_attributes = True

class BackupRestore(BaseModel):
    backup_id: int = Field(..., ge=1, description="ID of the backup to restore")
    restore_name: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Name for the restore operation"
    )