from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.api.deps import require_role
from app.models.enums import UserRole
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportOut

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/", response_model=ReportOut)
async def create_report(payload: ReportCreate, _: str = Depends(require_role(UserRole.admin)), db: AsyncSession = Depends(get_db)):
    r = Report(**payload.model_dump())
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return r

@router.get("/", response_model=list[ReportOut])
async def list_reports(_: str = Depends(require_role(UserRole.admin)), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Report))
    return res.scalars().all()
