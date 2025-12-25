"""
Review Tool
Retrieves and aggregates review information for rooms
"""
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.models.room import Room


async def get_room_reviews(
    db: AsyncSession,
    room_id: int,
    limit: int = 10
) -> List[dict]:
    """Get reviews for a specific room"""
    query = (
        select(Review)
        .where(Review.room_id == room_id)
        .order_by(Review.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    return [
        {
            "id": review.id,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at.isoformat() if review.created_at else None
        }
        for review in reviews
    ]


async def get_room_rating_summary(
    db: AsyncSession,
    room_id: int
) -> dict:
    """Get rating summary for a room"""
    # Average rating
    avg_query = select(func.avg(Review.rating)).where(Review.room_id == room_id)
    avg_result = await db.execute(avg_query)
    avg_rating = avg_result.scalar() or 0.0
    
    # Review count
    count_query = select(func.count(Review.id)).where(Review.room_id == room_id)
    count_result = await db.execute(count_query)
    review_count = count_result.scalar() or 0
    
    # Rating distribution
    distribution = {}
    for rating in range(1, 6):
        dist_query = select(func.count(Review.id)).where(
            Review.room_id == room_id,
            Review.rating >= rating,
            Review.rating < rating + 1
        )
        dist_result = await db.execute(dist_query)
        distribution[str(rating)] = dist_result.scalar() or 0
    
    return {
        "room_id": room_id,
        "average_rating": round(avg_rating, 1),
        "review_count": review_count,
        "rating_distribution": distribution
    }


async def get_highly_rated_rooms(
    db: AsyncSession,
    min_rating: float = 4.0,
    min_reviews: int = 1,
    limit: int = 20
) -> List[int]:
    """Get IDs of rooms with high ratings"""
    query = (
        select(Review.room_id, func.avg(Review.rating).label("avg_rating"), func.count(Review.id).label("count"))
        .group_by(Review.room_id)
        .having(func.avg(Review.rating) >= min_rating)
        .having(func.count(Review.id) >= min_reviews)
        .order_by(func.avg(Review.rating).desc())
        .limit(limit)
    )
    result = await db.execute(query)
    return [row[0] for row in result.fetchall()]
