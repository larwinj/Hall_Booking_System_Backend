from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
from datetime import date, datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.utils.search import search_rooms
from app.schemas.room import RoomOut
from app.schemas.search import UnavailableSlot, RoomAvailableResponse, AvailableSlot, RoomUnavailableResponse
from app.services.availability_service import AvailabilityService


router = APIRouter(prefix="/search", tags=["search"])


@router.get("/rooms", response_model=List[RoomOut], description="Access by everyone - Search available rooms by city, capacity, room type, and optional date/time slot")
async def search_rooms_api(
    city: str | None = None,
    date: date | None = None,
    start_time: str | None = None,  # HH:MM format
    end_time: str | None = None,    # HH:MM format
    capacity: int | None = None,
    room_type: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    if (date is None) != (start_time is None) or (date is None) != (end_time is None):
        raise HTTPException(400, "Date, start_time, and end_time must all be provided together or omitted")
    
    rooms = await search_rooms(
        db, 
        city=city, 
        date=date,
        start_time=start_time,
        end_time=end_time,
        capacity=capacity, 
        room_type=room_type
    )
    return rooms

@router.get("/rooms/{room_id}/unavailable-slots", 
           response_model=RoomUnavailableResponse,
           description="Access by everyone - Get all booked/unavailable time slots for a specific room on a given date")
async def get_room_unavailable_slots(
    room_id: int,
    search_date: date = Query(..., description="The date to check for unavailable slots (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
):
    try:
        unavailable_slots_data = await AvailabilityService.get_room_unavailable_slots(db, room_id, search_date)
        
        unavailable_slots = []
        for slot in unavailable_slots_data:
            unavailable_slots.append(UnavailableSlot(
                start_time=slot["start_time"].isoformat(),
                end_time=slot["end_time"].isoformat(),
                status=slot["status"]
            ))
        
        return RoomUnavailableResponse(
            room_id=room_id,
            date=search_date,
            unavailable_slots=unavailable_slots
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching unavailable slots: {str(e)}")

@router.get("/rooms/{room_id}/available-slots", 
           response_model=RoomAvailableResponse,
           description="Access by everyone - Get available time slots for a specific room on a given date")
async def get_room_available_slots(
    room_id: int,
    search_date: date = Query(..., description="The date to check for available slots (YYYY-MM-DD)"),
    operating_start: int = Query(8, ge=0, le=23, description="Operating hours start (0-23)"),
    operating_end: int = Query(22, ge=1, le=24, description="Operating hours end (1-24)"),
    db: AsyncSession = Depends(get_db),
):
    try:
        available_slots_data = await AvailabilityService.get_room_available_slots(
            db, room_id, search_date, (operating_start, operating_end)
        )
        
        available_slots = []
        for slot in available_slots_data:
            available_slots.append(AvailableSlot(
                start_time=slot["start_time"].isoformat(),
                end_time=slot["end_time"].isoformat()
            ))
        
        return RoomAvailableResponse(
            room_id=room_id,
            date=search_date,
            available_slots=available_slots
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching available slots: {str(e)}")

# @router.get("/rooms/{room_id}/check-availability",
#            description="Access by everyone - Check if a room is available for a specific time slot")
# async def check_room_availability(
#     room_id: int,
#     start_time: str = Query(..., description="Start time in ISO format (YYYY-MM-DDTHH:MM:SS)"),
#     end_time: str = Query(..., description="End time in ISO format (YYYY-MM-DDTHH:MM:SS)"),
#     exclude_booking_id: int | None = Query(None, description="Optional booking ID to exclude from check (for rescheduling)"),
#     db: AsyncSession = Depends(get_db),
# ):
#     try:
#         # Parse datetime strings and ensure they have timezone info
#         start_dt = datetime.fromisoformat(start_time)
#         end_dt = datetime.fromisoformat(end_time)
        
#         # If the parsed datetime doesn't have timezone info, assume UTC
#         if start_dt.tzinfo is None:
#             start_dt = start_dt.replace(tzinfo=timezone.utc)
#         if end_dt.tzinfo is None:
#             end_dt = end_dt.replace(tzinfo=timezone.utc)
        
#         is_available = await AvailabilityService.is_room_available(
#             db, room_id, start_dt, end_dt, exclude_booking_id
#         )
        
#         return {
#             "room_id": room_id,
#             "start_time": start_time,
#             "end_time": end_time,
#             "is_available": is_available
#         }
        
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error checking availability: {str(e)}")