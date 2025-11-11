from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract
from sqlalchemy.orm import joinedload
from collections import defaultdict
from datetime import datetime
from typing import Dict, Any, List
from app.models.enums import UserRole
from app.models.report_cache import ReportCache
from app.models.user import User
from bson import ObjectId
import motor.motor_asyncio
from app.db.mongodb import bookings_collection, reports_collection
from app.models.booking import Booking
from app.models.room import Room
from app.models.booking_customer import BookingCustomer
from app.models.booking_addon import BookingAddon
from app.models.venue import Venue
from app.schemas.reports import UserBookingSummary, RoomReport

async def mirror_booking_to_mongo(booking: Booking, db: AsyncSession):
    room_result = await db.execute(select(Room).where(Room.id == booking.room_id))
    
    room = room_result.scalar_one()
    customers_result = await db.execute(
        select(BookingCustomer).where(BookingCustomer.booking_id == booking.id)
    )
    customers = customers_result.scalars().all()

    # Fetch addons
    addons_result = await db.execute(
        select(BookingAddon).where(BookingAddon.booking_id == booking.id)
    )
    addons = addons_result.scalars().all()

    booking_doc = {
        "booking_id": str(booking.id),
        "venue_id": room.venue_id,
        "room_id": booking.room_id,
        "room_name": room.name,
        "room_type": room.type,
        "start_time": booking.start_time.isoformat(),
        "end_time": booking.end_time.isoformat(),
        "duration_hours": (booking.end_time - booking.start_time).total_seconds() / 3600.0,
        "status": booking.status.value,
        "total_cost": float(booking.total_cost),
        "customers": [
            {
                "user_id": c.user_id,
                "first_name": c.first_name,
                "last_name": c.last_name,
                "phone": c.phone,
            }
            for c in customers
        ],
        "addons": [
            {"addon_id": a.addon_id, "quantity": a.quantity, "subtotal": float(a.subtotal)}
            for a in addons
        ],
        "created_at": booking.created_at.isoformat(),
    }
    await bookings_collection.insert_one(booking_doc)

async def compute_monthly_report(venue_id: int, month_year: str, db: AsyncSession) -> Dict[str, Any]:
    
    parts = month_year.split('-')
    if len(parts) != 2:
        raise ValueError("month_year must be in YYYY-MM format")
    try:
        year = int(parts[0])
        month = int(parts[1])
        if not (1 <= month <= 12) or not (1900 <= year <= 2100):
            raise ValueError("Invalid year or month")
    except ValueError:
        raise ValueError("month_year must be valid YYYY-MM integers")
    
    stmt = select(Booking).options(
        joinedload(Booking.room),
        joinedload(Booking.customers),
        joinedload(Booking.addons)
    ).where(
        Booking.room_id.in_(select(Room.id).where(Room.venue_id == venue_id)),
        extract('year', Booking.start_time) == year,
        extract('month', Booking.start_time) == month,
        Booking.status != 'cancelled'
    )
    
    result = await db.execute(stmt)
    bookings = result.unique().scalars().all()
    
    if not bookings:
        venue_result = await db.execute(select(Venue).where(Venue.id == venue_id))
        venue = venue_result.scalar_one_or_none()
        if not venue:
            raise HTTPException(404, "Venue not found")
        
        rooms_result = await db.execute(select(Room).where(Room.venue_id == venue_id))
        rooms = rooms_result.scalars().all()
        
        return {
            'venue_id': venue_id,
            'venue_name': venue.name,
            'month_year': month_year,
            'total_bookings': 0,
            'total_revenue': 0.0,
            'rooms': [
                {
                    'room_id': r.id,
                    'room_name': r.name,
                    'room_type': r.type,
                    'total_bookings': 0,
                    'total_revenue': 0.0,
                    'avg_duration_hours': 0.0,
                    'users': []
                }
                for r in rooms
            ]
        }
    
    # Aggregate by room and user    
    room_data = defaultdict(lambda: {
        'total_bookings': 0,
        'total_revenue': 0.0,
        'avg_duration': 0.0,
        'users': defaultdict(lambda: {'total_bookings': 0, 'total_spent': 0.0, 'bookings': [], 'first_name': '', 'last_name': '', 'phone': ''})
    })
    
    total_bookings = 0
    total_revenue = 0.0
    
    for booking in bookings:
        room = booking.room
        duration = (booking.end_time - booking.start_time).total_seconds() / 3600.0
        
        room_key = booking.room_id
        room_data[room_key]['total_bookings'] += 1
        room_data[room_key]['total_revenue'] += booking.total_cost
        room_data[room_key]['avg_duration'] += duration
        total_bookings += 1
        total_revenue += booking.total_cost
        
        # Group by user (handle multiple customers per booking)
        for customer in booking.customers:
            user_key = str(customer.user_id) if customer.user_id is not None else f"guest_{customer.phone}"
            if not room_data[room_key]['users'][user_key]['first_name']:
                room_data[room_key]['users'][user_key]['first_name'] = customer.first_name
                room_data[room_key]['users'][user_key]['last_name'] = customer.last_name
                room_data[room_key]['users'][user_key]['phone'] = customer.phone
            
            room_data[room_key]['users'][user_key]['total_bookings'] += 1
            room_data[room_key]['users'][user_key]['total_spent'] += booking.total_cost
            room_data[room_key]['users'][user_key]['bookings'].append({
                'booking_id': booking.id,
                'date': booking.start_time.date().isoformat(),
                'duration': round(duration, 2),
                'cost': float(booking.total_cost),
                'addons': [{'addon_id': a.addon_id, 'quantity': a.quantity} for a in (booking.addons or [])]
            })
    
    for room_key in room_data:
        if room_data[room_key]['total_bookings'] > 0:
            room_data[room_key]['avg_duration'] /= room_data[room_key]['total_bookings']
        room_data[room_key]['users_list'] = [
            {
                'user_key': k,
                'first_name': v['first_name'],
                'last_name': v['last_name'],
                'phone': v['phone'],
                'total_bookings': v['total_bookings'],
                'total_spent': v['total_spent'],
                'bookings': v['bookings']
            }
            for k, v in room_data[room_key]['users'].items()
        ]
    
    venue_result = await db.execute(select(Venue).where(Venue.id == venue_id))
    venue = venue_result.scalar_one_or_none()
    if not venue:
        raise HTTPException(404, "Venue not found")
    
    rooms_result = await db.execute(select(Room).where(Room.venue_id == venue_id))
    rooms = rooms_result.scalars().all()
    room_map = {r.id: r for r in rooms}
    
    report = {
        'venue_id': venue_id,
        'venue_name': venue.name,
        'month_year': month_year,
        'total_bookings': total_bookings,
        'total_revenue': round(total_revenue, 2),
        'rooms': []
    }
    
    for room_id, data in room_data.items():
        room = room_map.get(room_id)
        if room:
            users_list = []
            for u in data['users_list']:
                user_key = u['user_key']
                # Parse user_id from user_key (now always str)
                user_id = None
                if not user_key.startswith('guest_'):
                    try:
                        user_id = int(user_key)
                    except ValueError:
                        user_id = None  # Invalid, treat as None
                
                summary = UserBookingSummary(
                    user_id=user_id,
                    first_name=u['first_name'] or 'Guest',
                    last_name=u['last_name'] or '',
                    phone=u['phone'] or '',
                    total_bookings=u['total_bookings'],
                    total_spent=round(u['total_spent'], 2),
                    bookings=u['bookings']
                )
                users_list.append(summary.model_dump())
            
            report['rooms'].append({
                'room_id': room_id,
                'room_name': room.name,
                'room_type': room.type,
                'total_bookings': data['total_bookings'],
                'total_revenue': round(data['total_revenue'], 2),
                'avg_duration_hours': round(data['avg_duration'], 2),
                'users': users_list
            })
    
    # Add empty rooms if no bookings
    for room in rooms:
        if room.id not in room_data:
            report['rooms'].append({
                'room_id': room.id,
                'room_name': room.name,
                'room_type': room.type,
                'total_bookings': 0,
                'total_revenue': 0.0,
                'avg_duration_hours': 0.0,
                'users': []
            })
    
    return report

async def get_or_compute_report(venue_id: int, month_year: str, db: AsyncSession, moderator: User) -> Dict[str, Any]:
    if moderator.assigned_venue_id != venue_id and moderator.role != UserRole.admin:
        raise HTTPException(403, "Unauthorized venue")
    
    # Check Postgres cache
    cache_stmt = select(ReportCache).where(
        ReportCache.venue_id == venue_id,
        ReportCache.month_year == month_year
    )
    cache = (await db.execute(cache_stmt)).scalar_one_or_none()
    
    if cache:
        # Fetch from Mongo
        doc = await reports_collection.find_one({"_id": ObjectId(cache.mongo_doc_id)})
        if doc:
            return doc
        # Cache invalid, recompute
    
    # Compute
    report_data = await compute_monthly_report(venue_id, month_year, db)
    
    # Store in Mongo
    doc_result = await reports_collection.insert_one(report_data)
    
    # Cache in Postgres
    new_cache = ReportCache(
        venue_id=venue_id,
        month_year=month_year,
        mongo_doc_id=str(doc_result.inserted_id)
    )
    db.add(new_cache)
    await db.commit()
    
    return report_data