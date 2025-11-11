from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.booking import Booking
from app.models.booking_customer import BookingCustomer
from app.models.enums import UserRole
from app.services.pdf_service import PDFService
from app.services.booking_data_service import BookingDataService

router = APIRouter(prefix="/booking_reports", tags=["booking_reports"])

@router.get(
    "/bookings/{booking_id}/download",
    description="Access by customers,moderators,admins - Download booking report as PDF"
)
async def download_booking_report(
    booking_id: int,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Download a professional PDF report for a specific booking
    """
    try:
        # Verify booking exists and user has permission
        booking = (await db.execute(select(Booking).where(Booking.id == booking_id))).scalar_one_or_none()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        # Check user permissions
        if user.role == UserRole.customer:
            linked = (await db.execute(
                select(BookingCustomer).where(
                    BookingCustomer.booking_id == booking_id,
                    BookingCustomer.user_id == user.id
                )
            )).scalar_one_or_none()
            
            if not linked:
                raise HTTPException(status_code=403, detail="Not allowed to access this booking report")

        # Fetch booking data asynchronously
        booking_data = await BookingDataService.get_booking_report_data(db, booking_id)
        
        # Generate PDF synchronously with the fetched data
        pdf_bytes = PDFService.generate_booking_report(booking_data)
        
        # Create response with PDF
        filename = f"booking_report_{booking_id}_{booking.created_at.strftime('%Y%m%d')}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes))
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@router.get(
    "/bookings/{booking_id}/preview",
    description="Access by customers,moderators,admins - Preview booking report in browser"
)
async def preview_booking_report(
    booking_id: int,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Preview booking report PDF in browser (inline)
    """
    try:
        # Verify booking exists and user has permission
        booking = (await db.execute(select(Booking).where(Booking.id == booking_id))).scalar_one_or_none()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if user.role == UserRole.customer:
            linked = (await db.execute(
                select(BookingCustomer).where(
                    BookingCustomer.booking_id == booking_id,
                    BookingCustomer.user_id == user.id
                )
            )).scalar_one_or_none()
            
            if not linked:
                raise HTTPException(status_code=403, detail="Not allowed to access this booking report")

        # Fetch booking data asynchronously
        booking_data = await BookingDataService.get_booking_report_data(db, booking_id)
        
        # Generate PDF synchronously with the fetched data
        pdf_bytes = PDFService.generate_booking_report(booking_data)
        
        # Create response with PDF for inline viewing
        filename = f"booking_report_{booking_id}_{booking.created_at.strftime('%Y%m%d')}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename={filename}",
                "Content-Length": str(len(pdf_bytes))
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")