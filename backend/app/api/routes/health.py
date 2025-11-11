from fastapi import APIRouter, Depends
from sqlalchemy import text
from app.db.session import AsyncSession, get_db

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/db",description="Access by Me(Developer) only.")
async def check_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return {"db_connected": bool(result.scalar())}