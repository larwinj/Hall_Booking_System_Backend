"""
Room Search Tool
Searches rooms from PostgreSQL database based on natural language extracted parameters
"""
from typing import Optional, List, Any
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.room import Room
from app.models.venue import Venue
from app.models.review import Review


async def search_rooms_by_criteria(
    db: AsyncSession,
    city: Optional[str] = None,
    capacity: Optional[int] = None,
    room_type: Optional[str] = None,
    min_rating: Optional[float] = None,
    amenities: Optional[List[str]] = None,
    max_rate: Optional[float] = None,
    venue_name: Optional[str] = None,
    limit: int = 20
) -> List[dict]:
    """
    Search rooms based on multiple criteria extracted from natural language queries.
    
    Args:
        db: Database session
        city: Filter by city (case-insensitive partial match)
        capacity: Minimum capacity required
        room_type: Type of room (Conference Room, Party Hall, etc.)
        min_rating: Minimum average rating
        amenities: List of required amenities
        max_rate: Maximum rate per hour
        venue_name: Filter by venue name (case-insensitive partial match)
        limit: Maximum number of results
        
    Returns:
        List of room dictionaries with venue and rating information
    """
    # Build base query with venue join
    query = (
        select(Room)
        .join(Venue, Room.venue_id == Venue.id)
        .options(joinedload(Room.venue))
        .where(Room.status == True)  # Only active rooms
    )
    
    conditions = []
    
    # City filter (case-insensitive partial match)
    if city:
        conditions.append(
            func.lower(Venue.city).contains(city.lower())
        )
    
    # Venue name filter
    if venue_name:
        conditions.append(
            func.lower(Venue.name).contains(venue_name.lower())
        )
    
    # Capacity filter (minimum)
    if capacity:
        conditions.append(Room.capacity >= capacity)
    
    # Room type filter (case-insensitive)
    if room_type:
        conditions.append(
            func.lower(Room.type).contains(room_type.lower())
        )
    
    # Max rate filter
    if max_rate:
        conditions.append(Room.rate_per_hour <= max_rate)
    
    # Apply conditions
    if conditions:
        query = query.where(and_(*conditions))
    
    # Execute query
    result = await db.execute(query.limit(limit))
    rooms = result.scalars().unique().all()
    
    # Get ratings for rooms if min_rating filter is applied
    room_data = []
    for room in rooms:
        # Get average rating for room
        rating_query = select(func.avg(Review.rating)).where(Review.room_id == room.id)
        rating_result = await db.execute(rating_query)
        avg_rating = rating_result.scalar() or 0.0
        
        # Check amenities if specified
        if amenities:
            room_amenities = [a.lower() for a in (room.amenities or [])]
            has_all_amenities = all(
                any(req.lower() in amenity for amenity in room_amenities)
                for req in amenities
            )
            if not has_all_amenities:
                continue
        
        # Filter by minimum rating if specified
        if min_rating and avg_rating < min_rating:
            continue
        
        room_dict = {
            "id": room.id,
            "name": room.name,
            "venue_id": room.venue_id,
            "venue_name": room.venue.name if room.venue else None,
            "city": room.venue.city if room.venue else None,
            "address": room.venue.address if room.venue else None,
            "capacity": room.capacity,
            "rate_per_hour": room.rate_per_hour,
            "type": room.type,
            "amenities": room.amenities or [],
            "description": room.description,
            "room_images": room.room_images or [],
            "status": room.status,
            "average_rating": round(avg_rating, 1)
        }
        room_data.append(room_dict)
    
    # Sort by rating if min_rating was specified
    if min_rating:
        room_data.sort(key=lambda x: x["average_rating"], reverse=True)
    
    return room_data


async def get_room_details(db: AsyncSession, room_id: int) -> Optional[dict]:
    """Get detailed information about a specific room"""
    query = (
        select(Room)
        .join(Venue, Room.venue_id == Venue.id)
        .options(joinedload(Room.venue))
        .where(Room.id == room_id)
    )
    result = await db.execute(query)
    room = result.scalar()
    
    if not room:
        return None
    
    # Get average rating
    rating_query = select(func.avg(Review.rating)).where(Review.room_id == room.id)
    rating_result = await db.execute(rating_query)
    avg_rating = rating_result.scalar() or 0.0
    
    # Get review count
    count_query = select(func.count(Review.id)).where(Review.room_id == room.id)
    count_result = await db.execute(count_query)
    review_count = count_result.scalar() or 0
    
    return {
        "id": room.id,
        "name": room.name,
        "venue_id": room.venue_id,
        "venue_name": room.venue.name if room.venue else None,
        "city": room.venue.city if room.venue else None,
        "address": room.venue.address if room.venue else None,
        "contact_phone": room.venue.contact_phone if room.venue else None,
        "contact_email": room.venue.contact_email if room.venue else None,
        "capacity": room.capacity,
        "rate_per_hour": room.rate_per_hour,
        "type": room.type,
        "amenities": room.amenities or [],
        "description": room.description,
        "room_images": room.room_images or [],
        "status": room.status,
        "average_rating": round(avg_rating, 1),
        "review_count": review_count
    }


async def get_available_cities(db: AsyncSession) -> List[str]:
    """Get list of all cities with venues"""
    query = select(Venue.city).distinct()
    result = await db.execute(query)
    cities = [row[0] for row in result.fetchall() if row[0]]
    return sorted(cities)


async def get_room_types(db: AsyncSession) -> List[str]:
    """Get list of all room types"""
    query = select(Room.type).distinct()
    result = await db.execute(query)
    types = [row[0] for row in result.fetchall() if row[0]]
    return sorted(types)
