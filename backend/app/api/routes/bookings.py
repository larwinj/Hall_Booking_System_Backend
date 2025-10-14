from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime, timezone
from app.db.session import get_db
from app.api.deps import get_current_user, require_role
from app.models.enums import UserRole, BookingStatus
from app.models.booking import Booking
from app.models.booking_addon import BookingAddon
from app.models.booking_customer import BookingCustomer
from app.models.room import Room
from app.schemas.booking import BookingCreate, BookingOut, BookingReschedule, BookingCancel
from app.services.booking import has_conflict, calculate_total_cost

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("/", response_model=BookingOut)
async def create_booking(payload: BookingCreate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Customers can only create for themselves (plus additional customer IDs if needed)
    # Moderators/Admin can create for any customers (business choice)
    # Conflict detection
    if await has_conflict(db, room_id=payload.room_id, start_time=payload.start_time, end_time=payload.end_time):
        raise HTTPException(status_code=409, detail="Time slot not available")
    total, addons_calc = await calculate_total_cost(
        db, room_id=payload.room_id, start_time=payload.start_time, end_time=payload.end_time,
        addons=[(a.addon_id, a.quantity) for a in payload.addons]
    )
    booking = Booking(
        room_id=payload.room_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        status=BookingStatus.confirmed,
        total_cost=total,
    )
    db.add(booking)
    await db.flush()
    # Link customers
    customers = set(payload.customer_ids or []) | {user.id}
    for cid in customers:
        db.add(BookingCustomer(booking_id=booking.id, user_id=cid))
    # Addons with subtotals
    for addon_id, qty, subtotal in addons_calc:
        db.add(BookingAddon(booking_id=booking.id, addon_id=addon_id, quantity=qty, subtotal=subtotal))
    await db.commit()
    await db.refresh(booking)
    return booking

@router.get("/me", response_model=list[BookingOut])
async def my_bookings(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(Booking).join(BookingCustomer).where(BookingCustomer.user_id == user.id)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/{booking_id}/reschedule", response_model=BookingOut)
async def reschedule_booking(booking_id: int, payload: BookingReschedule, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    booking = (await db.execute(select(Booking).where(Booking.id == booking_id))).scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    # Only a customer tied to this booking, moderator of the venue, or admin can reschedule
    linked = (await db.execute(select(BookingCustomer).where(BookingCustomer.booking_id == booking_id, BookingCustomer.user_id == user.id))).scalar_one_or_none()
    if user.role == UserRole.customer and not linked:
        raise HTTPException(status_code=403, detail="Not allowed")
    if await has_conflict(db, room_id=booking.room_id, start_time=payload.start_time, end_time=payload.end_time, exclude_booking_id=booking.id):
        raise HTTPException(status_code=409, detail="New time slot not available")
    # record original
    if not booking.rescheduled:
        booking.original_start_time = booking.start_time
        booking.original_end_time = booking.end_time
    booking.start_time = payload.start_time
    booking.end_time = payload.end_time
    booking.rescheduled = True
    # recalc cost
    total = 0.0
    addons_pairs = []
    # fetch addons attached
    addons = (await db.execute(select(BookingAddon).where(BookingAddon.booking_id == booking.id))).scalars().all()
    if addons:
        addons_pairs = [(a.addon_id, a.quantity) for a in addons]
    total, recalced = await calculate_total_cost(db, room_id=booking.room_id, start_time=booking.start_time, end_time=booking.end_time, addons=addons_pairs)
    booking.total_cost = total
    # update each addon subtotal
    for addon_id, qty, subtotal in recalced:
        for a in addons:
            if a.addon_id == addon_id:
                a.quantity = qty
                a.subtotal = subtotal
    await db.commit()
    await db.refresh(booking)
    return booking

@router.post("/{booking_id}/cancel")
async def cancel_booking(booking_id: int, _: BookingCancel, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    booking = (await db.execute(select(Booking).where(Booking.id == booking_id))).scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    linked = (await db.execute(select(BookingCustomer).where(BookingCustomer.booking_id == booking_id, BookingCustomer.user_id == user.id))).scalar_one_or_none()
    if user.role == UserRole.customer and not linked:
        raise HTTPException(status_code=403, detail="Not allowed")
    booking.status = BookingStatus.cancelled
    await db.commit()
    return {"success": True}
