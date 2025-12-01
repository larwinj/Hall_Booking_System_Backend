from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract,and_, or_
from sqlalchemy.orm import joinedload
from collections import defaultdict
from datetime import datetime,timedelta, date
from typing import Dict, Any, List
from app.models.enums import UserRole
from app.models.report_cache import ReportCache
from app.models.user import User
from bson import ObjectId
import motor.motor_asyncio
from app.db.mongodb import bookings_collection, reports_collection
from app.models.booking import Booking
from app.models.room import Room
from app.models.addon import Addon
from app.models.booking_customer import BookingCustomer
from app.models.booking_addon import BookingAddon
from app.models.venue import Venue
from app.schemas.reports import UserBookingSummary, RoomReport,  VenueAnalyticsReport

# from app.services.reports import get_or_compute_report, get_venue_analytics_report, get_location_analytics_report

from app.models.enums import BookingStatus

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

async def get_venue_analytics_report(
    db: AsyncSession, 
    venue_id: int, 
    days: int
) -> Dict[str, Any]:
    """
    Generate comprehensive analytics report for a venue for the last N days
    """
    # Calculate date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    # Get venue details
    venue_result = await db.execute(select(Venue).where(Venue.id == venue_id))
    venue = venue_result.scalar_one_or_none()
    if not venue:
        raise ValueError(f"Venue with ID {venue_id} not found")
    
    # Get all rooms for this venue
    rooms_result = await db.execute(select(Room).where(Room.venue_id == venue_id))
    rooms = rooms_result.scalars().all()
    room_ids = [room.id for room in rooms]
    
    # Base query for bookings in the date range
    bookings_query = select(Booking).where(
        and_(
            Booking.room_id.in_(room_ids),
            Booking.start_time >= start_date,
            Booking.start_time < end_date + timedelta(days=1),
            Booking.status == BookingStatus.confirmed
        )
    )
    
    bookings_result = await db.execute(bookings_query)
    bookings = bookings_result.scalars().all()
    
    # Total bookings and revenue
    total_bookings = len(bookings)
    total_revenue = sum(booking.total_cost for booking in bookings)
    average_booking_value = total_revenue / total_bookings if total_bookings > 0 else 0
    
    # Cancelled and rescheduled bookings
    cancelled_result = await db.execute(
        select(func.count(Booking.id)).where(
            and_(
                Booking.room_id.in_(room_ids),
                Booking.start_time >= start_date,
                Booking.start_time < end_date + timedelta(days=1),
                Booking.status == BookingStatus.cancelled
            )
        )
    )
    cancelled_bookings = cancelled_result.scalar_one()
    
    rescheduled_result = await db.execute(
        select(func.count(Booking.id)).where(
            and_(
                Booking.room_id.in_(room_ids),
                Booking.start_time >= start_date,
                Booking.start_time < end_date + timedelta(days=1),
                Booking.rescheduled == True
            )
        )
    )
    rescheduled_bookings = rescheduled_result.scalar_one()
    
    # Room performance
    room_performance = []
    for room in rooms:
        room_bookings = [b for b in bookings if b.room_id == room.id]
        room_revenue = sum(b.total_cost for b in room_bookings)
        
        # Calculate occupancy rate (simplified)
        total_possible_hours = days * 12  # Assuming 12 operating hours per day
        booked_hours = sum((b.end_time - b.start_time).total_seconds() / 3600 for b in room_bookings)
        occupancy_rate = (booked_hours / total_possible_hours) * 100 if total_possible_hours > 0 else 0
        
        room_performance.append({
            "room_id": room.id,
            "room_name": room.name,
            "total_bookings": len(room_bookings),
            "total_revenue": room_revenue,
            "occupancy_rate": round(occupancy_rate, 2),
            "average_booking_value": room_revenue / len(room_bookings) if room_bookings else 0
        })
    
    # Daily breakdown
    daily_breakdown = []
    current_date = start_date
    while current_date <= end_date:
        day_bookings = [b for b in bookings if b.start_time.date() == current_date]
        day_revenue = sum(b.total_cost for b in day_bookings)
        
        daily_breakdown.append({
            "date": current_date.isoformat(),
            "bookings": len(day_bookings),
            "revenue": day_revenue,
            "day_name": current_date.strftime("%A")
        })
        current_date += timedelta(days=1)
    
    # Customer statistics
    customers_result = await db.execute(
        select(BookingCustomer).where(
            BookingCustomer.booking_id.in_([b.id for b in bookings])
        )
    )
    all_customers = customers_result.scalars().all()
    
    unique_customers = set()
    customer_booking_count = {}
    
    for customer in all_customers:
        customer_key = f"{customer.first_name}_{customer.last_name}_{customer.phone}"
        unique_customers.add(customer_key)
        if customer_key in customer_booking_count:
            customer_booking_count[customer_key] += 1
        else:
            customer_booking_count[customer_key] = 1
    
    total_customers = len(unique_customers)
    repeat_customers = sum(1 for count in customer_booking_count.values() if count > 1)
    
    # Addon statistics
    addons_result = await db.execute(
        select(BookingAddon, Addon).join(
            Addon, BookingAddon.addon_id == Addon.id
        ).where(
            BookingAddon.booking_id.in_([b.id for b in bookings])
        )
    )
    
    addon_data = []
    addon_revenue = 0
    addon_popularity = {}
    
    for booking_addon, addon in addons_result:
        addon_revenue += booking_addon.subtotal
        
        if addon.name in addon_popularity:
            addon_popularity[addon.name] += booking_addon.quantity
        else:
            addon_popularity[addon.name] = booking_addon.quantity
    
    popular_addons = [
        {"addon_name": name, "total_quantity": quantity}
        for name, quantity in sorted(addon_popularity.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    # Peak hours analysis
    hour_distribution = {}
    for booking in bookings:
        hour = booking.start_time.hour
        if hour in hour_distribution:
            hour_distribution[hour] += 1
        else:
            hour_distribution[hour] = 1
    
    peak_hours = [
        {"hour": f"{hour:02d}:00", "bookings": count}
        for hour, count in sorted(hour_distribution.items(), key=lambda x: x[1], reverse=True)[:6]
    ]
    
    # Calculate overall occupancy rate
    total_possible_room_hours = len(rooms) * days * 12
    total_booked_hours = sum((b.end_time - b.start_time).total_seconds() / 3600 for b in bookings)
    overall_occupancy_rate = (total_booked_hours / total_possible_room_hours) * 100 if total_possible_room_hours > 0 else 0
    
    return {
        "venue_id": venue_id,
        "venue_name": venue.name,
        "period_days": days,
        "report_date_range": f"{start_date} to {end_date}",
        "total_bookings": total_bookings,
        "total_revenue": total_revenue,
        "average_booking_value": round(average_booking_value, 2),
        "occupancy_rate": round(overall_occupancy_rate, 2),
        "cancelled_bookings": cancelled_bookings,
        "rescheduled_bookings": rescheduled_bookings,
        "room_performance": room_performance,
        "daily_breakdown": daily_breakdown,
        "total_customers": total_customers,
        "repeat_customers": repeat_customers,
        "addon_revenue": addon_revenue,
        "popular_addons": popular_addons,
        "peak_hours": peak_hours
    }
    
async def get_location_analytics_report(
    db: AsyncSession, 
    city: str
) -> Dict[str, Any]:
    """
    Generate comprehensive analytics report for a specific city
    """
    # Get all venues in the city
    venues_result = await db.execute(
        select(Venue).where(func.lower(Venue.city) == func.lower(city))
    )
    venues = venues_result.scalars().all()
    
    if not venues:
        raise ValueError(f"No venues found in city: {city}")
    
    venue_ids = [venue.id for venue in venues]
    
    # Get all rooms for these venues
    rooms_result = await db.execute(
        select(Room).where(Room.venue_id.in_(venue_ids))
    )
    rooms = rooms_result.scalars().all()
    room_ids = [room.id for room in rooms]
    
    # Get all bookings for these rooms (last 365 days for comprehensive analysis)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)
    
    bookings_query = select(Booking).where(
        and_(
            Booking.room_id.in_(room_ids),
            Booking.start_time >= start_date,
            Booking.start_time < end_date + timedelta(days=1),
            Booking.status == BookingStatus.confirmed
        )
    )
    
    bookings_result = await db.execute(bookings_query)
    all_bookings = bookings_result.scalars().all()
    
    # Get all customers for these bookings
    customers_result = await db.execute(
        select(BookingCustomer).where(
            BookingCustomer.booking_id.in_([b.id for b in all_bookings])
        )
    )
    all_customers = customers_result.scalars().all()
    
    # Basic statistics
    total_bookings = len(all_bookings)
    total_revenue = sum(booking.total_cost for booking in all_bookings)
    average_booking_value = total_revenue / total_bookings if total_bookings > 0 else 0
    
    # Venue performance
    venue_performance = []
    for venue in venues:
        venue_rooms = [room for room in rooms if room.venue_id == venue.id]
        venue_room_ids = [room.id for room in venue_rooms]
        venue_bookings = [b for b in all_bookings if b.room_id in venue_room_ids]
        venue_revenue = sum(b.total_cost for b in venue_bookings)
        
        # Calculate occupancy for venue
        total_possible_hours = 365 * 12 * len(venue_rooms)  # 12 hours per day
        booked_hours = sum((b.end_time - b.start_time).total_seconds() / 3600 for b in venue_bookings)
        occupancy_rate = (booked_hours / total_possible_hours) * 100 if total_possible_hours > 0 else 0
        
        venue_performance.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "total_bookings": len(venue_bookings),
            "total_revenue": venue_revenue,
            "occupancy_rate": round(occupancy_rate, 2),
            "average_booking_value": venue_revenue / len(venue_bookings) if venue_bookings else 0,
            "room_count": len(venue_rooms)
        })
    
    # Room type analysis
    room_type_analysis = {}
    for room in rooms:
        room_type = room.type or "standard"
        room_bookings = [b for b in all_bookings if b.room_id == room.id]
        room_revenue = sum(b.total_cost for b in room_bookings)
        
        if room_type not in room_type_analysis:
            room_type_analysis[room_type] = {
                "total_bookings": 0,
                "total_revenue": 0,
                "room_count": 0
            }
        
        room_type_analysis[room_type]["total_bookings"] += len(room_bookings)
        room_type_analysis[room_type]["total_revenue"] += room_revenue
        room_type_analysis[room_type]["room_count"] += 1
    
    room_type_list = [
        {
            "room_type": room_type,
            "total_bookings": data["total_bookings"],
            "total_revenue": data["total_revenue"],
            "room_count": data["room_count"],
            "average_revenue_per_room": data["total_revenue"] / data["room_count"] if data["room_count"] > 0 else 0
        }
        for room_type, data in room_type_analysis.items()
    ]
    
    # Monthly trend (last 12 months)
    monthly_trend = []
    for i in range(12):
        month_date = end_date - timedelta(days=30*i)
        month_start = month_date.replace(day=1)
        if i == 0:
            month_end = end_date
        else:
            next_month = month_start + timedelta(days=32)
            month_end = next_month.replace(day=1) - timedelta(days=1)
        
        month_bookings = [b for b in all_bookings if month_start <= b.start_time.date() <= month_end]
        month_revenue = sum(b.total_cost for b in month_bookings)
        
        monthly_trend.append({
            "month": month_start.strftime("%Y-%m"),
            "bookings": len(month_bookings),
            "revenue": month_revenue,
            "month_name": month_start.strftime("%B %Y")
        })
    
    monthly_trend.reverse()  # Show oldest to newest
    
    # Customer demographics
    unique_customers = set()
    customer_city_distribution = {}
    
    for customer in all_customers:
        # Extract city from address (simple extraction)
        address_city = "Unknown"
        if customer.address and ',' in customer.address:
            address_parts = customer.address.split(',')
            if len(address_parts) >= 2:
                address_city = address_parts[-2].strip()
        
        customer_key = f"{customer.first_name}_{customer.last_name}_{customer.phone}"
        unique_customers.add(customer_key)
        
        if address_city in customer_city_distribution:
            customer_city_distribution[address_city] += 1
        else:
            customer_city_distribution[address_city] = 1
    
    customer_cities_list = [
        {"city": city, "customer_count": count}
        for city, count in sorted(customer_city_distribution.items(), key=lambda x: x[1], reverse=True)[:10]
    ]
    
    # Peak seasons (by month)
    monthly_booking_count = {}
    for booking in all_bookings:
        month_key = booking.start_time.strftime("%Y-%m")
        if month_key in monthly_booking_count:
            monthly_booking_count[month_key] += 1
        else:
            monthly_booking_count[month_key] = 1
    
    peak_seasons = [
        {
            "period": month,
            "bookings": count,
            "percentage": (count / total_bookings * 100) if total_bookings > 0 else 0
        }
        for month, count in sorted(monthly_booking_count.items(), key=lambda x: x[1], reverse=True)[:6]
    ]
    
    # Revenue distribution
    total_city_revenue = sum(venue["total_revenue"] for venue in venue_performance)
    revenue_distribution = {
        venue["venue_name"]: (venue["total_revenue"] / total_city_revenue * 100) if total_city_revenue > 0 else 0
        for venue in venue_performance
    }
    
    # Calculate overall occupancy rate for the city
    total_possible_city_hours = 365 * 12 * len(rooms)
    total_booked_city_hours = sum((b.end_time - b.start_time).total_seconds() / 3600 for b in all_bookings)
    overall_occupancy_rate = (total_booked_city_hours / total_possible_city_hours) * 100 if total_possible_city_hours > 0 else 0
    
    return {
        "city": city.title(),
        "total_venues": len(venues),
        "total_bookings": total_bookings,
        "total_revenue": total_revenue,
        "average_booking_value": round(average_booking_value, 2),
        "overall_occupancy_rate": round(overall_occupancy_rate, 2),
        "venue_performance": venue_performance,
        "room_type_analysis": room_type_list,
        "monthly_trend": monthly_trend,
        "total_customers": len(unique_customers),
        "customer_cities": customer_cities_list,
        "peak_seasons": peak_seasons,
        "revenue_distribution": revenue_distribution
    }