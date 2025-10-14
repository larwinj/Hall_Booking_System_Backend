from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from app.db.session import get_db
from app.api.deps import require_role, require_moderator_scope, get_current_user
from app.models.enums import UserRole
from app.models.venue import Venue
from app.models.user import User
from app.schemas.venue import VenueCreate, VenueUpdate, VenueOut

router = APIRouter(prefix="/venues", tags=["venues"])

@router.post("/", response_model=VenueOut)
async def create_venue(payload: VenueCreate, _: User = Depends(require_role(UserRole.moderator)), db: AsyncSession = Depends(get_db)):
    venue = Venue(**payload.model_dump())
    db.add(venue)
    await db.commit()
    await db.refresh(venue)
    return venue

@router.get("/", response_model=list[VenueOut])
async def list_venues(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Venue))
    return res.scalars().all()

@router.get("/{venue_id}", response_model=VenueOut)
async def get_venue(venue_id: int, db: AsyncSession = Depends(get_db)):
    venue = (await db.execute(select(Venue).where(Venue.id == venue_id))).scalar_one_or_none()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return venue

@router.patch("/{venue_id}", response_model=VenueOut)
async def update_venue(venue_id: int, payload: VenueUpdate, _: User = Depends(require_role(UserRole.moderator)), db: AsyncSession = Depends(get_db)):
    venue = (await db.execute(select(Venue).where(Venue.id == venue_id))).scalar_one_or_none()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(venue, k, v)
    await db.commit()
    await db.refresh(venue)
    return venue

@router.delete("/{venue_id}")
async def delete_venue(venue_id: int, _: User = Depends(require_role(UserRole.moderator)), db: AsyncSession = Depends(get_db)):
    venue = (await db.execute(select(Venue).where(Venue.id == venue_id))).scalar_one_or_none()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    await db.delete(venue)
    await db.commit()
    return {"success": True}
