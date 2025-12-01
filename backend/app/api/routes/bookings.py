from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select
from datetime import date, datetime, timezone
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.enums import UserRole, BookingStatus
from app.models.booking import Booking
from app.models.booking_addon import BookingAddon
from app.models.booking_customer import BookingCustomer
from app.models.room import Room
from app.schemas.booking import BookingCreate, BookingOut, BookingReschedule, BookingCancel, RescheduleResponse, RoomBookingsResponse
from app.services.booking import has_conflict, calculate_total_cost
from app.services.wallet_service import WalletService
from app.schemas.wallet import RefundCalculation
from app.schemas.booking_reschedule_history import BookingRescheduleHistoryOut
from app.models.user import User
from app.models.venue import Venue
from app.services.notification_service import NotificationService


router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("/", response_model=BookingOut, description="Access by customers,moderators,admins.")
async def create_booking(payload: BookingCreate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    full_start = payload.compute_start_datetime()
    full_end = payload.compute_end_datetime()

    if full_start <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Booking start time must be in the future.")

    if await has_conflict(db, room_id=payload.room_id, start_time=full_start, end_time=full_end):
        raise HTTPException(status_code=409, detail="Time slot not available - collision detected.")

    total, addons_calc = await calculate_total_cost(
        db, room_id=payload.room_id, start_time=full_start, end_time=full_end,
        addons=[(a.addon_id, a.quantity) for a in payload.addons]
    )

    booking = Booking(
        room_id=payload.room_id,
        start_time=full_start,
        end_time=full_end,
        status=BookingStatus.confirmed,
        total_cost=total,
    )
    db.add(booking)
    await db.flush()

    # Add customers with details
    for customer_data in payload.customers:
        bc = BookingCustomer(
            booking_id=booking.id,
            user_id=customer_data.user_id,
            first_name=customer_data.first_name,
            last_name=customer_data.last_name,
            email=customer_data.email,  # Add email
            address=customer_data.address,
            phone=customer_data.phone,
        )
        db.add(bc)

    # Add addons
    for addon_id, qty, subtotal in addons_calc:
        db.add(BookingAddon(booking_id=booking.id, addon_id=addon_id, quantity=qty, subtotal=subtotal))

    await db.commit()
    await db.refresh(booking)

    # Send booking confirmation notification (in background)
    try:
        await NotificationService.send_booking_confirmation_notification(db, booking.id)
    except Exception as e:
        print(f"Failed to send booking confirmation email: {str(e)}")
        # Don't fail the booking if email fails

    return booking

@router.get("/me", response_model=list[BookingOut],description="Access by customers")
async def my_bookings(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(Booking).join(BookingCustomer).where(BookingCustomer.user_id == user.id)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/", response_model=list[BookingOut], description="Access by moderators,admins - Get all bookings")
async def get_all_bookings(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Get all bookings for moderators and admins.
    Moderators see only bookings for their assigned venue.
    Admins see all bookings.
    """
    if user.role == UserRole.customer:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    if user.role == UserRole.moderator:
        if not user.assigned_venue_id:
            raise HTTPException(status_code=403, detail="No venue assigned to moderator")
        
        # Get all rooms for this moderator's venue
        rooms_query = select(Room).where(Room.venue_id == user.assigned_venue_id)
        rooms_result = await db.execute(rooms_query)
        rooms = rooms_result.scalars().all()
        room_ids = [r.id for r in rooms]
        
        # Get all bookings for these rooms
        bookings_query = select(Booking).where(Booking.room_id.in_(room_ids)) if room_ids else select(Booking).where(False)
        bookings_result = await db.execute(bookings_query)
        return bookings_result.scalars().all()
    
    # Admin: return all bookings
    result = await db.execute(select(Booking))
    return result.scalars().all()

@router.post("/{booking_id}/reschedule", response_model=RescheduleResponse, description="Access by customers,moderators,admins.")
async def reschedule_booking(
    booking_id: int, 
    payload: BookingReschedule, 
    user=Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    # Get the original booking
    booking = (await db.execute(select(Booking).where(Booking.id == booking_id))).scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if booking can be rescheduled
    if booking.rescheduled:
        raise HTTPException(status_code=400, detail="Booking has already been rescheduled once")

    # Check user permissions
    linked = (await db.execute(
        select(BookingCustomer).where(
            BookingCustomer.booking_id == booking_id, 
            BookingCustomer.user_id == user.id
        )
    )).scalar_one_or_none()
    
    if user.role == UserRole.customer and not linked:
        raise HTTPException(status_code=403, detail="Not allowed to reschedule this booking")

    # Calculate new datetime
    full_start = payload.compute_start_datetime()
    full_end = payload.compute_end_datetime()

    if full_start <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Rescheduled start time must be in the future.")

    # Determine which room to use for reschedule
    target_room_id = payload.new_room_id if payload.new_room_id else booking.room_id

    # Validate room change if applicable
    if payload.new_room_id and payload.new_room_id != booking.room_id:
        is_valid_room_change = await WalletService.validate_room_change(
            db, booking.room_id, payload.new_room_id
        )
        if not is_valid_room_change:
            raise HTTPException(
                status_code=400, 
                detail="Cannot change to a room in a different venue"
            )

    # Check for conflicts in the new time slot
    if await has_conflict(db, room_id=target_room_id, start_time=full_start, end_time=full_end, exclude_booking_id=booking.id):
        raise HTTPException(status_code=409, detail="New time slot not available - collision detected.")

    try:
        # Store original booking details for history
        original_room_id = booking.room_id
        original_start_time = booking.start_time
        original_end_time = booking.end_time
        original_total_cost = booking.total_cost

        # Calculate cost breakdown for reschedule
        cost_breakdown = await WalletService.get_reschedule_cost_breakdown(
            db, booking, target_room_id, full_start, full_end
        )

        # Update booking with new details
        booking.start_time = full_start
        booking.end_time = full_end
        booking.room_id = target_room_id
        booking.rescheduled = True
        booking.total_cost = cost_breakdown["new_cost"]
        booking.updated_at = datetime.now(timezone.utc)

        # Update addon subtotals if room changed or time changed significantly
        if payload.new_room_id or cost_breakdown["recalculated_addons"]:
            # Remove existing addons and add recalculated ones
            await db.execute(
                BookingAddon.__table__.delete().where(BookingAddon.booking_id == booking.id)
            )
            
            for addon_id, quantity, subtotal in cost_breakdown["recalculated_addons"]:
                new_addon = BookingAddon(
                    booking_id=booking.id,
                    addon_id=addon_id,
                    quantity=quantity,
                    subtotal=subtotal
                )
                db.add(new_addon)

        # Handle price differences through wallet
        refund_amount = 0
        additional_amount = 0
        price_difference = cost_breakdown["price_difference"]
        message = "Booking rescheduled successfully."

        if cost_breakdown["is_refund"]:
            # Process refund to wallet
            transaction, refund_amount, actual_price_diff = await WalletService.process_reschedule_refund(
                db, booking, user.id, original_total_cost, cost_breakdown["new_cost"],
                f"Reschedule refund: Room {original_room_id} → Room {target_room_id}, " +
                f"{original_start_time.strftime('%Y-%m-%d %H:%M')} → {full_start.strftime('%Y-%m-%d %H:%M')}"
            )
            message += f" Refund of ₹{refund_amount:.2f} has been added to your wallet."
        
        elif cost_breakdown["price_difference"] > 0:
            # Process payment from wallet
            transaction, additional_amount, actual_price_diff = await WalletService.process_reschedule_payment(
                db, booking, user.id, original_total_cost, cost_breakdown["new_cost"],
                f"Reschedule additional payment: Room {original_room_id} → Room {target_room_id}, " +
                f"{original_start_time.strftime('%Y-%m-%d %H:%M')} → {full_start.strftime('%Y-%m-%d %H:%M')}"
            )
            
            if additional_amount > 0:
                message += f" Additional payment of ₹{additional_amount:.2f} is required."
            else:
                message += f" Additional payment of ₹{cost_breakdown['price_difference']:.2f} has been deducted from your wallet."

        # Create reschedule history record
        await WalletService.create_reschedule_history(
            db=db,
            booking=booking,
            original_room_id=original_room_id,
            original_start_time=original_start_time,
            original_end_time=original_end_time,
            original_total_cost=original_total_cost,
            new_room_id=target_room_id,
            new_start_time=full_start,
            new_end_time=full_end,
            new_total_cost=cost_breakdown["new_cost"],
            price_difference=price_difference,
            refund_amount=refund_amount,
            additional_amount=additional_amount,
            reschedule_reason=getattr(payload, 'reason', None)
        )

        await db.commit()
        await db.refresh(booking)

        # Send reschedule notification (in background)
        try:
            original_start_str = original_start_time.strftime("%Y-%m-%d %H:%M")
            original_end_str = original_end_time.strftime("%Y-%m-%d %H:%M")
            
            await NotificationService.send_booking_rescheduled_notification(
                db=db,
                booking_id=booking.id,
                original_start_time=original_start_str,
                original_end_time=original_end_str,
                price_difference=price_difference
            )
        except Exception as e:
            print(f"Failed to send reschedule notification email: {str(e)}")

        return RescheduleResponse(
            booking=booking,
            price_difference=price_difference,
            refund_amount=refund_amount,
            additional_amount=additional_amount,
            message=message
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing reschedule: {str(e)}")
    
@router.post("/{booking_id}/cancel", description="Access by customers,moderators,admins.")
async def cancel_booking(
    booking_id: int, 
    payload: BookingCancel, 
    user=Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    booking = (await db.execute(select(Booking).where(Booking.id == booking_id))).scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Check if user has permission to cancel this booking
    linked = (await db.execute(
        select(BookingCustomer).where(
            BookingCustomer.booking_id == booking_id, 
            BookingCustomer.user_id == user.id
        )
    )).scalar_one_or_none()
    
    if user.role == UserRole.customer and not linked:
        raise HTTPException(status_code=403, detail="Not allowed to cancel this booking")

    # Check if booking is already cancelled
    if booking.status == BookingStatus.cancelled:
        raise HTTPException(status_code=400, detail="Booking is already cancelled")

    # Calculate refund amount before processing
    refund_amount, cancellation_fee, policy_description = await WalletService.calculate_refund_amount(booking)
    hours_until_booking = (booking.start_time - datetime.now(timezone.utc)).total_seconds() / 3600

    refund_calculation = RefundCalculation(
        original_amount=booking.total_cost,
        refund_percentage=(refund_amount / booking.total_cost) * 100,
        refund_amount=refund_amount,
        cancellation_fee=cancellation_fee,
        hours_until_booking=hours_until_booking,
        refund_policy_applied=policy_description
    )

    # Process refund to user's wallet
    try:
        if refund_amount > 0:
            transaction, actual_refund, actual_policy = await WalletService.process_booking_refund(
                db, booking, user.id, payload.reason
            )
            
            # Update refund calculation with actual processed values
            refund_calculation.refund_amount = actual_refund
            refund_calculation.refund_policy_applied = actual_policy
            refund_calculation.refund_percentage = (actual_refund / booking.total_cost) * 100
            refund_calculation.cancellation_fee = booking.total_cost - actual_refund

        # Update booking status
        booking.status = BookingStatus.cancelled
        await db.commit()

        response_message = "Booking cancelled successfully."
        if refund_amount > 0:
            response_message += f" Refund of ₹{refund_amount:.2f} has been added to your wallet."
        else:
            response_message += " No refund available as per cancellation policy."

        # Send cancellation notification (in background)
        try:
            await NotificationService.send_booking_cancelled_notification(
                db=db,
                booking_id=booking.id,
                reason=payload.reason,
                refund_amount=refund_amount,
                refund_policy=policy_description
            )
        except Exception as e:
            print(f"Failed to send cancellation notification email: {str(e)}")

        return {
            "success": True, 
            "message": response_message,
            "refund_details": refund_calculation
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing cancellation: {str(e)}")

@router.get("/{booking_id}/reschedule-history",response_model=list[BookingRescheduleHistoryOut],description="Access by customers,moderators,admins - Get reschedule history for a booking")
async def get_booking_reschedule_history(
    booking_id: int,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the reschedule history for a specific booking
    """
    # Verify booking exists and user has permission
    booking = (await db.execute(select(Booking).where(Booking.id == booking_id))).scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Check user permissions
    linked = (await db.execute(
        select(BookingCustomer).where(
            BookingCustomer.booking_id == booking_id, 
            BookingCustomer.user_id == user.id
        )
    )).scalar_one_or_none()
    
    if user.role == UserRole.customer and not linked:
        raise HTTPException(status_code=403, detail="Not allowed to view this booking's history")

    history = await WalletService.get_booking_reschedule_history(db, booking_id)
    return history

@router.get("/room-bookings", response_model=RoomBookingsResponse, description="Access by moderators,admins")
async def get_room_bookings_by_date(
    room_id: int = Query(..., description="Room ID to fetch bookings for"),
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(None, description="End date (YYYY-MM-DD) - optional, defaults to start_date"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get bookings for a specific room within a date range.
    If only start_date is provided, returns bookings for that single day.
    """
    # Check if user has permission (moderator or admin)
    if user.role not in [UserRole.moderator, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    if end_date is None:
        end_date = start_date
    
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date")
    
    room_result = await db.execute(
        select(Room).where(Room.id == room_id)
    )
    room = room_result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # For moderators, check if room belongs to their assigned venue
    if user.role == UserRole.moderator:
        if not user.assigned_venue_id:
            raise HTTPException(status_code=403, detail="No venue assigned to moderator")
        if room.venue_id != user.assigned_venue_id:
            raise HTTPException(status_code=403, detail="Room does not belong to your assigned venue")
    
    start_datetime = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_datetime = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)
    
    bookings_query = select(Booking).where(
        and_(
            Booking.room_id == room_id,
            Booking.start_time >= start_datetime,
            Booking.start_time <= end_datetime
        )
    ).order_by(Booking.start_time)
    
    bookings_result = await db.execute(bookings_query)
    bookings = bookings_result.scalars().all()
    
    # Get room name from venue
    venue_result = await db.execute(
        select(Venue.name).where(Venue.id == room.venue_id)
    )
    venue_name = venue_result.scalar_one_or_none() or "Unknown Venue"
    
    return RoomBookingsResponse(
        room_id=room_id,
        room_name=room.name,
        start_date=start_date,
        end_date=end_date,
        total_bookings=len(bookings),
        bookings=bookings
    )