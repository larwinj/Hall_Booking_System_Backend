from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.services.email_service import EmailService
from app.models.booking import Booking
from app.models.booking_customer import BookingCustomer
from app.models.room import Room
from app.models.venue import Venue
from app.models.user import User

class NotificationService:
    
    @staticmethod
    async def send_booking_confirmation_notification(
        db: AsyncSession,
        booking_id: int
    ) -> bool:
        """Send booking confirmation notification to all customers"""
        try:
            # Get booking details
            booking_result = await db.execute(
                select(Booking).where(Booking.id == booking_id)
            )
            booking = booking_result.scalar_one_or_none()
            
            if not booking:
                return False
            
            # Get room and venue details
            room_result = await db.execute(
                select(Room, Venue).join(Venue, Room.venue_id == Venue.id).where(Room.id == booking.room_id)
            )
            room_venue = room_result.first()
            
            if not room_venue:
                return False
            
            room, venue = room_venue
            
            # Get all customers for this booking
            customers_result = await db.execute(
                select(BookingCustomer).where(BookingCustomer.booking_id == booking_id)
            )
            customers = customers_result.scalars().all()
            
            # Send email to each customer
            success_count = 0
            for customer in customers:
                # Format datetime for display
                start_time = booking.start_time.strftime("%Y-%m-%d %H:%M")
                end_time = booking.end_time.strftime("%Y-%m-%d %H:%M")
                
                success = await EmailService.send_booking_confirmation(
                    customer_email=customer.email,  # You might need to add email field to BookingCustomer
                    customer_name=f"{customer.first_name} {customer.last_name}",
                    booking_id=booking.id,
                    venue_name=venue.name,
                    room_name=room.name,
                    start_time=start_time,
                    end_time=end_time,
                    total_cost=booking.total_cost,
                    status=booking.status.value
                )
                
                if success:
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            print(f"Error sending booking confirmation: {str(e)}")
            return False
    
    @staticmethod
    async def send_booking_rescheduled_notification(
        db: AsyncSession,
        booking_id: int,
        original_start_time: Optional[str] = None,
        original_end_time: Optional[str] = None,
        price_difference: float = 0
    ) -> bool:
        """Send booking rescheduled notification"""
        try:
            # Similar implementation to confirmation but for reschedule
            booking_result = await db.execute(
                select(Booking).where(Booking.id == booking_id)
            )
            booking = booking_result.scalar_one_or_none()
            
            if not booking:
                return False
            
            room_result = await db.execute(
                select(Room, Venue).join(Venue, Room.venue_id == Venue.id).where(Room.id == booking.room_id)
            )
            room_venue = room_result.first()
            
            if not room_venue:
                return False
            
            room, venue = room_venue
            
            customers_result = await db.execute(
                select(BookingCustomer).where(BookingCustomer.booking_id == booking_id)
            )
            customers = customers_result.scalars().all()
            
            success_count = 0
            for customer in customers:
                start_time = booking.start_time.strftime("%Y-%m-%d %H:%M")
                end_time = booking.end_time.strftime("%Y-%m-%d %H:%M")
                
                success = await EmailService.send_booking_rescheduled(
                    customer_email=customer.email,
                    customer_name=f"{customer.first_name} {customer.last_name}",
                    booking_id=booking.id,
                    venue_name=venue.name,
                    room_name=room.name,
                    start_time=start_time,
                    end_time=end_time,
                    total_cost=booking.total_cost,
                    original_start_time=original_start_time,
                    original_end_time=original_end_time,
                    price_difference=price_difference
                )
                
                if success:
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            print(f"Error sending reschedule notification: {str(e)}")
            return False
    
    @staticmethod
    async def send_booking_cancelled_notification(
        db: AsyncSession,
        booking_id: int,
        reason: Optional[str] = None,
        refund_amount: float = 0,
        refund_policy: str = ""
    ) -> bool:
        """Send booking cancellation notification"""
        try:
            # Similar implementation for cancellation
            booking_result = await db.execute(
                select(Booking).where(Booking.id == booking_id)
            )
            booking = booking_result.scalar_one_or_none()
            
            if not booking:
                return False
            
            room_result = await db.execute(
                select(Room, Venue).join(Venue, Room.venue_id == Venue.id).where(Room.id == booking.room_id)
            )
            room_venue = room_result.first()
            
            if not room_venue:
                return False
            
            room, venue = room_venue
            
            customers_result = await db.execute(
                select(BookingCustomer).where(BookingCustomer.booking_id == booking_id)
            )
            customers = customers_result.scalars().all()
            
            success_count = 0
            for customer in customers:
                start_time = booking.start_time.strftime("%Y-%m-%d %H:%M")
                end_time = booking.end_time.strftime("%Y-%m-%d %H:%M")
                
                success = await EmailService.send_booking_cancelled(
                    customer_email=customer.email,
                    customer_name=f"{customer.first_name} {customer.last_name}",
                    booking_id=booking.id,
                    venue_name=venue.name,
                    room_name=room.name,
                    start_time=start_time,
                    end_time=end_time,
                    reason=reason,
                    refund_amount=refund_amount,
                    refund_policy=refund_policy
                )
                
                if success:
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            print(f"Error sending cancellation notification: {str(e)}")
            return False