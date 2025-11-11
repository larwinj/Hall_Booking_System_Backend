from typing import List, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.booking import Booking
from app.models.room import Room
from app.models.addon import Addon
from app.models.enums import BookingStatus
from fastapi import HTTPException

async def has_conflict(
    db: AsyncSession,
    room_id: int,
    start_time: datetime,
    end_time: datetime,
    exclude_booking_id: int | None = None
) -> bool:
    stmt = select(Booking).where(
        Booking.room_id == room_id,
        Booking.status != BookingStatus.cancelled,
        Booking.start_time < end_time,
        Booking.end_time > start_time,
    )
    if exclude_booking_id:
        stmt = stmt.where(Booking.id != exclude_booking_id)
    result = await db.execute(stmt)
    return result.scalars().first() is not None

async def calculate_total_cost(
    db: AsyncSession,
    room_id: int,
    start_time: datetime,
    end_time: datetime,
    addons: List[Tuple[int, int]]
) -> Tuple[float, List[Tuple[int, int, float]]]:
    # Fetch room
    room_result = await db.execute(select(Room).where(Room.id == room_id))
    room = room_result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Calculate base cost
    duration_hours = (end_time - start_time).total_seconds() / 3600.0
    base_cost = room.rate_per_hour * duration_hours

    # Calculate addons cost with validation
    addons_total = 0.0
    addons_calc = []
    for addon_id, qty in addons:
        addon_result = await db.execute(select(Addon).where(Addon.id == addon_id))
        addon = addon_result.scalar_one_or_none()
        if not addon:
            raise HTTPException(status_code=404, detail=f"Addon {addon_id} not found")
        if addon.venue_id != room.venue_id:
            raise HTTPException(status_code=400, detail=f"Addon {addon_id} mismatch - does not belong to the venue of room {room_id}")
        subtotal = addon.price * qty
        addons_total += subtotal
        addons_calc.append((addon_id, qty, subtotal))

    total = base_cost + addons_total
    return total, addons_calc