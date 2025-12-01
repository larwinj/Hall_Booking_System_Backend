from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_user, require_role
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.reports import VenueAnalyticsReport, VenueMonthlyReport
from app.services.reports import get_location_analytics_report, get_or_compute_report, get_venue_analytics_report
from app.utils.mongo_utils import ObjectId
from app.schemas.venue import LocationAnalyticsReport  # Or from bson

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
    
    
@router.get("/venue-report", response_model=VenueAnalyticsReport, description="Access by admins only")
async def report_of_venue(
    venue_id: int,
    days: int = Query(7, ge=1, le=365, description="Number of days for the report (1-365)"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.admin))
):
    try:
        report = await get_venue_analytics_report(db, venue_id, days)
        return VenueAnalyticsReport(**report)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
    
    
    # NEED TO DO THE LOACTION BAASED ONE.
    
@router.get("/location-analytics", response_model=LocationAnalyticsReport, description="Access by admins only")
async def location_based_analytics(
    city: str = Query(..., description="City name for analytics"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.admin))
):
    """
    Get comprehensive analytics report for all venues in a specific city
    """
    try:
        report = await get_location_analytics_report(db, city)
        return LocationAnalyticsReport(**report)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating location analytics: {str(e)}")