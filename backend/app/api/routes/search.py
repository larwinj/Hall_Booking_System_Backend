from fastapi import APIRouter, Depends, Query
from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.utils.search import search_rooms
from app.schemas.room import RoomOut

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/rooms", response_model=list[RoomOut])
async def search_rooms_api(
    city: str | None = None,
    date: datetime | None = None,
    capacity: int | None = None,
    amenities: List[str] | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    rooms = await search_rooms(db, city=city, date=date, capacity=capacity, amenities=amenities)
    return rooms