from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta, date
from typing import Dict, Any, List
from app.models.booking import Booking
from app.models.room import Room
from app.models.venue import Venue
from app.models.enums import BookingStatus

class VenueReportService:
    
    @staticmethod
    async def get_venue_range_report(
        db: AsyncSession, 
        venue_id: int, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """
        Generate venue report for a specific date range
        """
        # Validate date range
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date")
        
        # Get venue details
        venue_result = await db.execute(select(Venue).where(Venue.id == venue_id))
        venue = venue_result.scalar_one_or_none()
        if not venue:
            raise ValueError(f"Venue with ID {venue_id} not found")
        
        # Get all rooms for this venue
        rooms_result = await db.execute(select(Room).where(Room.venue_id == venue_id))
        rooms = rooms_result.scalars().all()
        room_ids = [room.id for room in rooms]
        
        # Convert dates to datetime for query
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Get all bookings in the date range
        bookings_query = select(Booking).where(
            and_(
                Booking.room_id.in_(room_ids),
                Booking.start_time >= start_datetime,
                Booking.start_time <= end_datetime
            )
        )
        
        bookings_result = await db.execute(bookings_query)
        all_bookings = bookings_result.scalars().all()
        
        # Calculate basic statistics
        total_bookings = len(all_bookings)
        confirmed_bookings = len([b for b in all_bookings if b.status == BookingStatus.confirmed])
        cancelled_bookings = len([b for b in all_bookings if b.status == BookingStatus.cancelled])
        pending_bookings = len([b for b in all_bookings if b.status == BookingStatus.pending])
        rescheduled_bookings = len([b for b in all_bookings if b.rescheduled])
        
        # Calculate revenue (only from confirmed bookings)
        confirmed_bookings_list = [b for b in all_bookings if b.status == BookingStatus.confirmed]
        total_revenue = sum(booking.total_cost for booking in confirmed_bookings_list)
        average_booking_value = total_revenue / confirmed_bookings if confirmed_bookings > 0 else 0
        
        # Room-wise breakdown
        room_breakdown = []
        for room in rooms:
            room_bookings = [b for b in all_bookings if b.room_id == room.id]
            room_confirmed = [b for b in room_bookings if b.status == BookingStatus.confirmed]
            room_revenue = sum(b.total_cost for b in room_confirmed)
            
            room_breakdown.append({
                "room_id": room.id,
                "room_name": room.name,
                "total_bookings": len(room_bookings),
                "confirmed_bookings": len(room_confirmed),
                "cancelled_bookings": len([b for b in room_bookings if b.status == BookingStatus.cancelled]),
                "total_revenue": room_revenue,
                "occupancy_rate": len(room_confirmed) / len(room_bookings) * 100 if room_bookings else 0
            })
        
        # Daily trend
        daily_trend = []
        current_date = start_date
        while current_date <= end_date:
            day_bookings = [b for b in all_bookings if b.start_time.date() == current_date]
            day_confirmed = [b for b in day_bookings if b.status == BookingStatus.confirmed]
            day_revenue = sum(b.total_cost for b in day_confirmed)
            
            daily_trend.append({
                "date": current_date.isoformat(),
                "total_bookings": len(day_bookings),
                "confirmed_bookings": len(day_confirmed),
                "revenue": day_revenue,
                "day_name": current_date.strftime("%A")
            })
            current_date += timedelta(days=1)
        
        # Status distribution
        status_distribution = {
            "confirmed": confirmed_bookings,
            "cancelled": cancelled_bookings,
            "pending": pending_bookings
        }
        
        # Peak hours analysis (only from confirmed bookings)
        hour_distribution = {}
        for booking in confirmed_bookings_list:
            hour = booking.start_time.hour
            if hour in hour_distribution:
                hour_distribution[hour] += 1
            else:
                hour_distribution[hour] = 1
        
        peak_hours = [
            {
                "hour": f"{hour:02d}:00-{(hour+1):02d}:00",
                "bookings": count,
                "percentage": (count / confirmed_bookings * 100) if confirmed_bookings > 0 else 0
            }
            for hour, count in sorted(hour_distribution.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        return {
            "venue_id": venue_id,
            "venue_name": venue.name,
            "start_date": start_date,
            "end_date": end_date,
            "total_bookings": total_bookings,
            "total_revenue": total_revenue,
            "confirmed_bookings": confirmed_bookings,
            "cancelled_bookings": cancelled_bookings,
            "pending_bookings": pending_bookings,
            "rescheduled_bookings": rescheduled_bookings,
            "average_booking_value": round(average_booking_value, 2),
            "room_breakdown": room_breakdown,
            "daily_trend": daily_trend,
            "status_distribution": status_distribution,
            "peak_hours": peak_hours
        }