from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.api.deps import require_role
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[UserOut])
async def list_users(_: User = Depends(require_role(UserRole.admin)), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User))
    return res.scalars().all()
