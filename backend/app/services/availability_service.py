from datetime import date, datetime, time, timezone
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.models.booking import Booking
from app.models.room import Room
from app.models.enums import BookingStatus

class AvailabilityService:
    
    @staticmethod
    async def get_room_unavailable_slots(
        db: AsyncSession, 
        room_id: int, 
        search_date: date
    ) -> List[Dict[str, Any]]:
        
        
        room_result = await db.execute(select(Room).where(Room.id == room_id))
        room = room_result.scalar_one_or_none()
        
        if not room:
            raise ValueError(f"Room with ID {room_id} not found")

        # Calculate the start and end of the search date WITH timezone info
        start_of_day = datetime.combine(search_date, time.min).replace(tzinfo=timezone.utc)
        end_of_day = datetime.combine(search_date, time.max).replace(tzinfo=timezone.utc)

        # Query for confirmed bookings that overlap with the search date
        stmt = select(Booking).where(
            and_(
                Booking.room_id == room_id,
                Booking.status == BookingStatus.confirmed,
                or_(
                    # Booking starts and ends on the same day as search date
                    and_(
                        Booking.start_time >= start_of_day,
                        Booking.end_time <= end_of_day
                    ),
                    # Booking starts before search date and ends during search date
                    and_(
                        Booking.start_time < start_of_day,
                        Booking.end_time > start_of_day,
                        Booking.end_time <= end_of_day
                    ),
                    # Booking starts during search date and ends after search date
                    and_(
                        Booking.start_time >= start_of_day,
                        Booking.start_time < end_of_day,
                        Booking.end_time > end_of_day
                    ),
                    # Booking spans across the entire search date (starts before and ends after)
                    and_(
                        Booking.start_time < start_of_day,
                        Booking.end_time > end_of_day
                    )
                )
            )
        ).order_by(Booking.start_time)

        result = await db.execute(stmt)
        bookings = result.scalars().all()

        # Convert bookings to unavailable slots
        unavailable_slots = []
        for booking in bookings:
            # For display purposes, we only show the portion of the booking that falls within the search date
            slot_start = max(booking.start_time, start_of_day)
            slot_end = min(booking.end_time, end_of_day)
            
            unavailable_slots.append({
                "start_time": slot_start,
                "end_time": slot_end,
                "status": booking.status.value,
                "booking_id": booking.id
            })

        return unavailable_slots

    @staticmethod
    async def get_room_available_slots(
        db: AsyncSession, 
        room_id: int, 
        search_date: date,
        operating_hours: tuple = (8, 22)  # Default: 8 AM to 10 PM
    ) -> List[Dict[str, datetime]]:
        
        # Get unavailable slots first
        unavailable_slots = await AvailabilityService.get_room_unavailable_slots(db, room_id, search_date)
        
        # Define operating hours WITH timezone info
        operating_start = datetime.combine(search_date, time(operating_hours[0], 0)).replace(tzinfo=timezone.utc)
        operating_end = datetime.combine(search_date, time(operating_hours[1], 0)).replace(tzinfo=timezone.utc)
        
        # If no bookings, the entire operating hours are available
        if not unavailable_slots:
            return [{
                "start_time": operating_start,
                "end_time": operating_end
            }]
        
        # Sort unavailable slots by start time
        unavailable_slots.sort(key=lambda x: x["start_time"])
        
        available_slots = []
        
        # Check before first booking
        first_booking_start = unavailable_slots[0]["start_time"]
        if operating_start < first_booking_start:
            available_slots.append({
                "start_time": operating_start,
                "end_time": first_booking_start
            })
        
        # Check between bookings
        for i in range(len(unavailable_slots) - 1):
            current_booking_end = unavailable_slots[i]["end_time"]
            next_booking_start = unavailable_slots[i + 1]["start_time"]
            
            if current_booking_end < next_booking_start:
                available_slots.append({
                    "start_time": current_booking_end,
                    "end_time": next_booking_start
                })
        
        # Check after last booking
        last_booking_end = unavailable_slots[-1]["end_time"]
        if last_booking_end < operating_end:
            available_slots.append({
                "start_time": last_booking_end,
                "end_time": operating_end
            })
        
        return available_slots

    @staticmethod
    async def is_room_available(
        db: AsyncSession,
        room_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_booking_id: int | None = None
    ) -> bool:
        
        # Verify room exists
        room_result = await db.execute(select(Room).where(Room.id == room_id))
        room = room_result.scalar_one_or_none()
        
        if not room:
            raise ValueError(f"Room with ID {room_id} not found")

        # Ensure both start_time and end_time have timezone info
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)

        # Query for conflicting bookings
        stmt = select(Booking).where(
            and_(
                Booking.room_id == room_id,
                Booking.status == BookingStatus.confirmed,
                or_(
                    # New booking starts during existing booking
                    and_(
                        Booking.start_time <= start_time,
                        Booking.end_time > start_time
                    ),
                    # New booking ends during existing booking
                    and_(
                        Booking.start_time < end_time,
                        Booking.end_time >= end_time
                    ),
                    # New booking completely contains existing booking
                    and_(
                        Booking.start_time >= start_time,
                        Booking.end_time <= end_time
                    ),
                    # Existing booking completely contains new booking
                    and_(
                        Booking.start_time <= start_time,
                        Booking.end_time >= end_time
                    )
                )
            )
        )

        if exclude_booking_id:
            stmt = stmt.where(Booking.id != exclude_booking_id)

        result = await db.execute(stmt)
        conflicting_booking = result.scalar_one_or_none()

        return conflicting_booking is None

    @staticmethod
    async def get_room_availability_for_period(
        db: AsyncSession,
        room_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[date, List[Dict[str, Any]]]:
        
        from datetime import timedelta
        
        availability = {}
        current_date = start_date
        
        while current_date <= end_date:
            unavailable_slots = await AvailabilityService.get_room_unavailable_slots(db, room_id, current_date)
            availability[current_date] = unavailable_slots
            current_date += timedelta(days=1)
        
        return availability