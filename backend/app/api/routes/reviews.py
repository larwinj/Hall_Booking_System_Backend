from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.api.deps import get_current_user, require_role
from app.models.review import Review
from app.models.booking import Booking
from app.models.booking_customer import BookingCustomer
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewOut
from app.models.enums import UserRole

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/", response_model=ReviewOut)
async def create_or_update_review(payload: ReviewCreate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Create a new review or update existing one for a booking.
    Only the user who made the booking can review it.
    """
    # Verify the booking exists and belongs to the user
    booking = (await db.execute(select(Booking).where(Booking.id == payload.booking_id))).scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Verify user is the customer of this booking
    customer = (await db.execute(
        select(BookingCustomer)
        .where(BookingCustomer.booking_id == payload.booking_id)
        .where(BookingCustomer.user_id == user.id)
    )).scalar_one_or_none()
    
    if not customer:
        raise HTTPException(status_code=403, detail="You can only review your own bookings")
    
    # Check if booking is completed
    if booking.status != "completed":
        raise HTTPException(status_code=400, detail="You can only review completed bookings")
    
    # Check if review already exists for this booking
    existing_review = (await db.execute(
        select(Review).where(Review.booking_id == payload.booking_id)
    )).scalar_one_or_none()
    
    if existing_review:
        # Update existing review
        existing_review.rating = payload.rating
        existing_review.comment = payload.comment
        await db.commit()
        await db.refresh(existing_review)
        return existing_review
    else:
        # Create new review
        review = Review(
            user_id=user.id,
            booking_id=payload.booking_id,
            room_id=payload.room_id,
            rating=payload.rating,
            comment=payload.comment
        )
        db.add(review)
        await db.commit()
        await db.refresh(review)
        return review

@router.get("/booking/{booking_id}", response_model=ReviewOut | None)
async def get_review_by_booking(booking_id: int, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Get the review for a specific booking.
    Returns null if no review exists.
    """
    review = (await db.execute(
        select(Review).where(Review.booking_id == booking_id)
    )).scalar_one_or_none()
    return review

@router.get("/room/{room_id}", response_model=list[ReviewOut])
async def list_room_reviews(room_id: int, db: AsyncSession = Depends(get_db)):
    """Get all reviews for a room"""
    res = await db.execute(select(Review).where(Review.room_id == room_id))
    return res.scalars().all()

@router.delete("/delete")
async def delete_review(review_id: int, _: str = Depends(require_role(UserRole.admin)), db: AsyncSession = Depends(get_db)):
    cur_review = (await db.execute(select(Review).where(Review.id == review_id))).scalar_one_or_none()
    if not cur_review:
        raise HTTPException(status_code=404, detail="Review not found")
    await db.delete(cur_review)
    await db.commit()
    return {"Message": "Review deleted successfully"}