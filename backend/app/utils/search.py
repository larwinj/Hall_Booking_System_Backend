from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload
from typing import List
from datetime import datetime, date, timezone
from app.models.room import Room
from app.models.venue import Venue
from app.models.booking import Booking
from app.models.enums import BookingStatus

async def search_rooms(
    db: AsyncSession,
    *,
    city: str | None,
    date: date | None,
    start_time: str | None,
    end_time: str | None,
    capacity: int | None,
    room_type: str | None,
    fallback_min_results: int = 3,
):
    full_start = None
    full_end = None
    if date and start_time and end_time:
        try:
            start_t = datetime.strptime(start_time, '%H:%M').time()
            end_t = datetime.strptime(end_time, '%H:%M').time()
            full_start = datetime.combine(date, start_t, tzinfo=timezone.utc)
            full_end = datetime.combine(date, end_t, tzinfo=timezone.utc)
            if full_end <= full_start:
                raise ValueError("end_time must be after start_time")
            now = datetime.now(timezone.utc)
            if full_start <= now:
                raise ValueError("Date and time must be in the future")
        except ValueError as e:
            raise ValueError(f"Invalid date/time: {str(e)}")
    elif date or start_time or end_time:
        raise ValueError("Date, start_time, and end_time must all be provided together")

    stmt = select(Room).join(Venue, Room.venue_id == Venue.id)
    if city:
        stmt = stmt.where(func.lower(Venue.city) == func.lower(city))
    if capacity:
        stmt = stmt.where(Room.capacity >= capacity)
    if room_type:
        stmt = stmt.where(func.lower(Room.type) == func.lower(room_type))

    # If date/time provided, filter available rooms (no conflicts)
    if full_start and full_end:
        # Subquery for conflicting bookings
        conflict_subq = select(Booking.room_id).where(
            and_(
                Booking.start_time < full_end,
                Booking.end_time > full_start,
                Booking.status != BookingStatus.cancelled
            )
        ).scalar_subquery()
        stmt = stmt.where(Room.id.notin_(conflict_subq))

    rooms = (await db.execute(stmt)).scalars().all()

    if len(rooms) >= fallback_min_results or not city:
        return rooms

    stmt_fb = select(Room).join(Venue, Room.venue_id == Venue.id)
    if city:
        stmt_fb = stmt_fb.where(func.lower(Venue.city).like(f"%{city.lower()}%"))
    if capacity:
        stmt_fb = stmt_fb.where(Room.capacity >= max(1, int(capacity * 0.8)))
    if room_type:
        stmt_fb = stmt_fb.where(func.lower(Room.type) == func.lower(room_type))

    if full_start and full_end:
        conflict_subq_fb = select(Booking.room_id).where(
            and_(
                Booking.start_time < full_end,
                Booking.end_time > full_start,
                Booking.status != BookingStatus.cancelled
            )
        ).scalar_subquery()
        stmt_fb = stmt_fb.where(Room.id.notin_(conflict_subq_fb))

    rooms_fb = (await db.execute(stmt_fb)).scalars().all()
    return list({r.id: r for r in rooms + rooms_fb}.values())