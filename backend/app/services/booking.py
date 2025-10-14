from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime
from app.models.booking import Booking
from app.models.booking_addon import BookingAddon
from app.models.room import Room
from app.models.addon import Addon
from app.models.enums import BookingStatus


async def has_conflict(db: AsyncSession, *, room_id: int, start_time: datetime, end_time: datetime, exclude_booking_id: int | None = None) -> bool:
    stmt = select(Booking).where(
        Booking.room_id == room_id,
        Booking.status != BookingStatus.cancelled,
        Booking.start_time < end_time,
        Booking.end_time > start_time,
    )
    if exclude_booking_id:
        stmt = stmt.where(Booking.id != exclude_booking_id)
    res = await db.execute(stmt)
    return res.scalars().first() is not None

async def calculate_total_cost(db: AsyncSession, *, room_id: int, start_time: datetime, end_time: datetime, addons: list[tuple[int, int]]):
    # duration in hours
    res = await db.execute(select(Room).where(Room.id == room_id))
    room = res.scalars().first()
    if not room:
        raise ValueError("Room not found")
    seconds = (end_time - start_time).total_seconds()
    hours = max(1, int((seconds + 3599) // 3600))
    room_cost = room.rate_per_hour * hours

    addon_total = 0.0
    per_addon_subtotals: list[tuple[int, int, float]] = []
    if addons:
        addon_ids = [a_id for a_id, _ in addons]
        addons_db = (await db.execute(select(Addon).where(Addon.id.in_(addon_ids)))).scalars().all()
        idx = {a.id: a for a in addons_db}
        for a_id, qty in addons:
            addon = idx.get(a_id)
            if not addon:
                raise ValueError(f"Addon {a_id} not found")
            subtotal = addon.price * max(1, qty)
            addon_total += subtotal
            per_addon_subtotals.append((a_id, max(1, qty), subtotal))
    return room_cost + addon_total, per_addon_subtotals
