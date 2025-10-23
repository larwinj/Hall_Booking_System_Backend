from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from datetime import datetime
from app.models.room import Room
from app.models.venue import Venue

async def search_rooms(
    db: AsyncSession,
    *,
    city: str | None,
    date: datetime | None,
    capacity: int | None,
    amenities: List[str] | None,
    fallback_min_results: int = 3,
):
    stmt = select(Room).join(Venue, Room.venue_id == Venue.id)
    if city:
        stmt = stmt.where(func.lower(Venue.city) == func.lower(city))
    if capacity:
        stmt = stmt.where(Room.capacity >= capacity)
    if amenities:
        for am in amenities:
            stmt = stmt.where(func.array_position(Room.amenities, am) != None)

    rooms = (await db.execute(stmt)).scalars().all()

    if len(rooms) >= fallback_min_results or not city:
        return rooms

    # fallback: broaden capacity tolerance and perform case-insensitive partial city match
    stmt_fb = select(Room).join(Venue, Room.venue_id == Venue.id).where(func.lower(Venue.city).like(f"%{city.lower()}%"))
    if capacity:
        stmt_fb = stmt_fb.where(Room.capacity >= max(1, int(capacity * 0.8)))
    rooms_fb = (await db.execute(stmt_fb)).scalars().all()
    return list({r.id: r for r in rooms + rooms_fb}.values())
