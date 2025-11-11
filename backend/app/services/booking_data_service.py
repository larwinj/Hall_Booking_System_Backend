from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
from app.models.booking import Booking
from app.models.room import Room
from app.models.venue import Venue
from app.models.booking_customer import BookingCustomer
from app.models.booking_addon import BookingAddon
from app.models.addon import Addon
from app.models.booking_reschedule_history import BookingRescheduleHistory

class BookingDataService:
    
    @staticmethod
    async def get_booking_report_data(db: AsyncSession, booking_id: int) -> Dict[str, Any]:
        """
        Fetch all booking-related data for PDF generation
        """
        # Get booking
        booking_result = await db.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        booking = booking_result.scalar_one_or_none()
        
        if not booking:
            raise ValueError(f"Booking with ID {booking_id} not found")
        
        # Get room
        room_result = await db.execute(
            select(Room).where(Room.id == booking.room_id)
        )
        room = room_result.scalar_one_or_none()
        
        if not room:
            raise ValueError(f"Room not found for booking {booking_id}")
        
        # Get venue through room
        venue_result = await db.execute(
            select(Venue).where(Venue.id == room.venue_id)
        )
        venue = venue_result.scalar_one_or_none()
        
        if not venue:
            raise ValueError(f"Venue not found for room {room.id}")
        
        # Get customers
        customers_result = await db.execute(
            select(BookingCustomer).where(BookingCustomer.booking_id == booking_id)
        )
        customers = customers_result.scalars().all()
        
        if not customers:
            raise ValueError(f"No customers found for booking {booking_id}")
        
        # Get addons with details
        addons_result = await db.execute(
            select(BookingAddon, Addon).join(
                Addon, BookingAddon.addon_id == Addon.id
            ).where(BookingAddon.booking_id == booking_id)
        )
        addons_data = []
        
        for booking_addon, addon in addons_result:
            addons_data.append({
                'name': addon.name,
                'quantity': booking_addon.quantity,
                'unit_price': addon.price,
                'subtotal': booking_addon.subtotal
            })
        
        # Get reschedule history (if any)
        reschedule_history_result = await db.execute(
            select(BookingRescheduleHistory)
            .where(BookingRescheduleHistory.booking_id == booking_id)
            .order_by(BookingRescheduleHistory.created_at.desc())
        )
        reschedule_history = reschedule_history_result.scalars().all()
        
        # Calculate room duration and costs
        room_duration = (booking.end_time - booking.start_time).total_seconds() / 3600
        room_cost = room.rate_per_hour * room_duration
        addons_cost = sum(addon['subtotal'] for addon in addons_data)
        
        return {
            'booking': {
                'id': booking.id,
                'status': booking.status.value,
                'created_at': booking.created_at,
                'total_cost': booking.total_cost,
                'rescheduled': booking.rescheduled,
                'start_time': booking.start_time,
                'end_time': booking.end_time,
            },
            'room': {
                'name': room.name,
                'type': room.type,
                'capacity': room.capacity,
                'rate_per_hour': room.rate_per_hour,
                'amenities': room.amenities,
                'description': room.description
            },
            'venue': {
                'name': venue.name,
                'address': venue.address,
                'city': venue.city,
                'state': venue.state,
                'country': venue.country,
                'postal_code': venue.postal_code
            },
            'customers': [
                {
                    'first_name': customer.first_name,
                    'last_name': customer.last_name,
                    'phone': customer.phone,
                    'address': customer.address
                }
                for customer in customers
            ],
            'addons': addons_data,
            'reschedule_history': [
                {
                    'original_start_time': history.original_start_time,
                    'original_end_time': history.original_end_time,
                    'new_start_time': history.new_start_time,
                    'new_end_time': history.new_end_time,
                    'created_at': history.created_at,
                    'price_difference': history.price_difference
                }
                for history in reschedule_history
            ],
            'cost_breakdown': {
                'room_duration': room_duration,
                'room_cost': room_cost,
                'addons_cost': addons_cost,
                'total_cost': booking.total_cost
            }
        }