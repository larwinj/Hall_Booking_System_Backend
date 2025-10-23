from typing import List, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.booking import Booking
from app.models.room import Room
from app.models.addon import Addon
from app.models.enums import BookingStatus

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
    room_result = await db.execute(select(Room).where(Room.id == room_id))
    room = room_result.scalar_one_or_none()
    if not room:
        raise ValueError("Room not found")
    duration_hours = (end_time - start_time).total_seconds() / 3600.0
    base_cost = room.rate_per_hour * duration_hours
    addons_calc = []
    addons_total = 0.0
    for addon_id, qty in addons:
        addon_result = await db.execute(select(Addon).where(Addon.id == addon_id))
        addon = addon_result.scalar_one_or_none()
        if not addon or addon.venue_id != room.venue_id:
            raise ValueError(f"Invalid addon {addon_id}")
        subtotal = addon.price * qty
        addons_total += subtotal
        addons_calc.append((addon_id, qty, subtotal))
    total = base_cost + addons_total
    return total, addons_calc