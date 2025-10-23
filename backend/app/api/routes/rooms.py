from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.api.deps import get_current_user, require_role
from app.models.enums import UserRole
from app.models.room import Room
from app.models.addon import Addon
from app.schemas.room import RoomCreate, RoomUpdate, RoomOut

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.post("/", response_model=RoomOut)
async def create_room(payload: RoomCreate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user.role not in [UserRole.moderator, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if user.role == UserRole.moderator and user.assigned_venue_id != payload.venue_id:
        raise HTTPException(status_code=403, detail="Cannot create room outside assigned venue")
    room = Room(**payload.model_dump(exclude={'addons'}))
    db.add(room)
    await db.flush()
    for addon_data in payload.addons:
        addon = Addon(venue_id=room.venue_id, **addon_data.model_dump())
        db.add(addon)
    await db.commit()
    await db.refresh(room)
    return room

@router.get("/", response_model=list[RoomOut])
async def list_rooms(venue_id: int | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(Room)
    if venue_id:
        stmt = stmt.where(Room.venue_id == venue_id)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/{room_id}", response_model=RoomOut)
async def get_room(room_id: int, db: AsyncSession = Depends(get_db)):
    room = (await db.execute(select(Room).where(Room.id == room_id))).scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.patch("/{room_id}", response_model=RoomOut)
async def update_room(room_id: int, payload: RoomUpdate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    room = (await db.execute(select(Room).where(Room.id == room_id))).scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if user.role == UserRole.moderator and user.assigned_venue_id != room.venue_id:
        raise HTTPException(status_code=403, detail="Cannot update room outside assigned venue")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(room, k, v)
    await db.commit()
    await db.refresh(room)
    return room

@router.delete("/{room_id}")
async def delete_room(room_id: int, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    room = (await db.execute(select(Room).where(Room.id == room_id))).scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if user.role == UserRole.moderator and user.assigned_venue_id != room.venue_id:
        raise HTTPException(status_code=403, detail="Cannot delete room outside assigned venue")
    await db.delete(room)
    await db.commit()
    return {"success": True}