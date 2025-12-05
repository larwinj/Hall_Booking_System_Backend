from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.enums import UserRole
from app.models.addon import Addon
from app.schemas.addon import AddonCreate, AddonUpdate, AddonOut

from app.models.user import User
from app.models.room import Room

router = APIRouter(prefix="/addons", tags=["addons"])

@router.post("/", response_model=AddonOut,description="Access by moderators,admins")
async def create_addon(payload: AddonCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user.role not in [UserRole.moderator, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if user.role == UserRole.moderator and payload.venue_id != user.assigned_venue_id:
        raise HTTPException(status_code=403, detail="Cannot create addon outside assigned venue")
    
    # If room_id provided, ensure it exists and belongs to the same venue
    if payload.room_id is not None:
        room = (await db.execute(select(Room).where(Room.id == payload.room_id))).scalar_one_or_none()
        if not room or room.venue_id != payload.venue_id:
            raise HTTPException(status_code=400, detail="Invalid room_id for given venue")
    
    addon = Addon(**payload.model_dump())
    db.add(addon)
    await db.commit()
    await db.refresh(addon)
    return addon

@router.get("/", response_model=list[AddonOut],description="Access by moderators,customers,admins.")
async def list_addons(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Addon))
    return res.scalars().all()

@router.get("/by-room/{room_id}", response_model=list[AddonOut], description="Access by customers,moderators,admins - Get addons for a specific room")
async def get_addons_by_room(room_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get all addons for a specific room.
    Returns addons where room_id matches OR room_id is NULL (venue-level addons).
    """
    from sqlalchemy import or_
    
    # Verify room exists
    room = (await db.execute(select(Room).where(Room.id == room_id))).scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Get room-specific addons AND venue-level addons (room_id is NULL)
    stmt = select(Addon).where(
        and_(
            Addon.venue_id == room.venue_id,
            or_(
                Addon.room_id == room_id,
                Addon.room_id.is_(None)
            )
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@router.patch("/{addon_id}", response_model=AddonOut,description="Access by moderators,admins")
async def update_addon(addon_id: int, payload: AddonUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user.role not in [UserRole.moderator, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    addon = (await db.execute(select(Addon).where(Addon.id == addon_id))).scalar_one_or_none()
    if not addon:
        raise HTTPException(status_code=404, detail="Addon not found")
    if user.role == UserRole.moderator and user.assigned_venue_id != addon.venue_id:
        raise HTTPException(status_code=403, detail="Cannot update addon outside assigned venue")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(addon, k, v)
    await db.commit()
    await db.refresh(addon)
    return addon

@router.delete("/{addon_id}",description="Access by moderators,admins")
async def delete_addon(addon_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user.role not in [UserRole.moderator, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    addon = (await db.execute(select(Addon).where(Addon.id == addon_id))).scalar_one_or_none()
    if not addon:
        raise HTTPException(status_code=404, detail="Addon not found")
    if user.role == UserRole.moderator and user.assigned_venue_id != addon.venue_id:
        raise HTTPException(status_code=403, detail="Cannot delete addon outside assigned venue")
    await db.delete(addon)
    await db.commit()
    return {"success": True}