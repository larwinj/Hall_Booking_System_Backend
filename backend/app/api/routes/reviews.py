from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.api.deps import get_current_user, require_role
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewOut
from app.models.enums import UserRole

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/", response_model=ReviewOut)
async def create_review(payload: ReviewCreate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    rev = Review(user_id=user.id, room_id=payload.room_id, rating=payload.rating, comment=payload.comment)
    db.add(rev)
    await db.commit()
    await db.refresh(rev)
    return rev

@router.get("/room/{room_id}", response_model=list[ReviewOut])
async def list_room_reviews(room_id: int, db: AsyncSession = Depends(get_db)):
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