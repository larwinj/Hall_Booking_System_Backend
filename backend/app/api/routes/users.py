from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.api.deps import require_role
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserAdminCreate, UserOut
from app.core.security import get_password_hash

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut, description="Access only by the admin users.")
async def create_user(payload: UserAdminCreate, _: User = Depends(require_role(UserRole.admin)), db: AsyncSession = Depends(get_db)):
    existing = (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_dict = payload.model_dump()
    user_dict['hashed_password'] = get_password_hash(user_dict.pop('password'))
    if payload.role != UserRole.moderator:
        user_dict['assigned_venue_id'] = None
    user = User(**user_dict)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.get("/", response_model=list[UserOut],description="Access only by the admin users.")
async def list_users(_: User = Depends(require_role(UserRole.admin)), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User))
    return res.scalars().all()


@router.delete("/delete",description="Access only by the admin users.")
async def delete_user(user_id: int, _: User = Depends(require_role(UserRole.admin)), db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
    return {"success": True}