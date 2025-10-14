from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.favorite import Favorite
from app.schemas.favorite import FavoriteCreate, FavoriteOut

router = APIRouter(prefix="/favorites", tags=["favorites"])

@router.post("/", response_model=FavoriteOut)
async def add_favorite(payload: FavoriteCreate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    existing = (await db.execute(select(Favorite).where(Favorite.user_id == user.id, Favorite.room_id == payload.room_id))).scalar_one_or_none()
    if existing:
        return existing
    fav = Favorite(user_id=user.id, room_id=payload.room_id)
    db.add(fav)
    await db.commit()
    await db.refresh(fav)
    return fav

@router.get("/", response_model=list[FavoriteOut])
async def list_favorites(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Favorite).where(Favorite.user_id == user.id))
    return res.scalars().all()

@router.delete("/{favorite_id}")
async def remove_favorite(favorite_id: int, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    fav = (await db.execute(select(Favorite).where(Favorite.id == favorite_id, Favorite.user_id == user.id))).scalar_one_or_none()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")
    await db.delete(fav)
    await db.commit()
    return {"success": True}
