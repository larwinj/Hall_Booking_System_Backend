from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import json
import logging

from app.db.session import get_db
from app.api.deps import get_current_user, require_role
from app.models.enums import UserRole
from app.models.user import User
from app.models.backup import Backup
from app.schemas.backup import BackupCreate, BackupOut, BackupRestore
from app.services.backup_service import BackupService
from app.services.vercel_blob_service import VercelBlobService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/backup", tags=["backup"])

@router.post("/create", response_model=BackupOut, description="Access only by admin users")
async def create_backup(
    payload: BackupCreate,
    background_tasks: BackgroundTasks,
    user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):
    try:
        logger.info(f"Creating backup: {payload.name}")
        backup = await BackupService.save_backup(db, payload.name, payload.description)
        logger.info(f"Backup created successfully: {backup.id}, Vercel URL: {backup.vercel_url}")
        return backup
    except Exception as e:
        logger.error(f"Backup creation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Backup creation failed: {str(e)}")

@router.get("/", response_model=List[BackupOut], description="Access only by admin users")
async def list_backups(
    skip: int = 0,
    limit: int = 100,
    user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):
    """
    List all available backups
    """
    backups = await BackupService.list_backups(db, skip, limit)
    return backups

@router.get("/{backup_id}", response_model=BackupOut, description="Access only by admin users")
async def get_backup(
    backup_id: int,
    user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific backup details
    """
    backup = await BackupService.get_backup(db, backup_id)
    if not backup:
        raise HTTPException(status_code=404, detail="Backup not found")
    return backup

@router.delete("/{backup_id}", description="Access only by admin users")
async def delete_backup(
    backup_id: int,
    user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):
    success = await BackupService.delete_backup(db, backup_id)
    if not success:
        raise HTTPException(status_code=404, detail="Backup not found")
    
    return {"success": True, "message": "Backup deleted successfully"}

@router.post("/restore", description="Access only by admin users")
async def restore_backup(
    payload: BackupRestore,
    user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):
    try:
        backup = await BackupService.get_backup(db, payload.backup_id)
        if not backup:
            raise HTTPException(status_code=404, detail="Backup not found")
        
        # which would involve clearing existing data and restoring from backup
        # Epothaiku ethu just return the output as a message
        
        return {
            "success": True,
            "message": f"Restore operation '{payload.restore_name}' initiated from backup '{backup.name}'",
            "backup_data_available": True,
            "backup_metadata": backup.backup_data.get('metadata', {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore operation failed: {str(e)}")

@router.get("/{backup_id}/download", description="Access only by admin users")
async def download_backup(
    backup_id: int,
    user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):
    backup = await BackupService.get_backup(db, backup_id)
    if not backup:
        raise HTTPException(status_code=404, detail="Backup not found")
    
    return {
        "filename": f"backup_{backup.id}_{backup.created_at.date()}.json",
        "backup_data": backup.backup_data
    }
    
@router.get("/{backup_id}/download-vercel", description="Access only by admin users - Download backup from Vercel Blob")
async def download_backup_from_vercel(
    backup_id: int,
    user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):
    """
    Download backup directly from Vercel Blob Storage
    """
    backup = await BackupService.get_backup(db, backup_id)
    if not backup:
        raise HTTPException(status_code=404, detail="Backup not found")
    
    if not backup.vercel_filename:
        raise HTTPException(status_code=404, detail="Backup not found in Vercel storage")
    
    try:
        backup_data = await VercelBlobService.download_backup_from_vercel(backup.vercel_filename)
        
        return {
            "filename": backup.vercel_filename,
            "vercel_url": backup.vercel_url,
            "backup_data": backup_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading from Vercel: {str(e)}")