from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_user, require_role
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.reports import VenueMonthlyReport
from app.services.reports import get_or_compute_report
from app.utils.mongo_utils import ObjectId  # Or from bson

router = APIRouter(prefix="/analyticsreports", tags=["analyticsreports"])

@router.get("/monthly", response_model=VenueMonthlyReport,description="Access by moderators")
async def get_monthly_report(
    month_year: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.moderator, UserRole.admin))
):
    # Quick format check
    if len(month_year) != 7 or month_year.count('-') != 1:
        raise HTTPException(400, "month_year must be in YYYY-MM format")
    
    venue_id = user.assigned_venue_id
    if not venue_id:
        raise HTTPException(403, "No assigned venue for moderator")
    
    try:
        report = await get_or_compute_report(venue_id, month_year, db, user)
        return VenueMonthlyReport(**report)
    except ValueError as e:
        raise HTTPException(400, f"Invalid month-year: {str(e)}")