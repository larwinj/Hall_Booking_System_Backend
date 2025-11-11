from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from typing import Dict, Any, List
import json
import logging

from app.models.user import User
from app.models.venue import Venue
from app.models.room import Room
from app.models.booking import Booking
from app.models.booking_customer import BookingCustomer
from app.models.booking_addon import BookingAddon
from app.models.addon import Addon
from app.models.review import Review
from app.models.query import Query
from app.models.report import Report
from app.models.backup import Backup
from app.services.vercel_blob_service import VercelBlobService

logger = logging.getLogger(__name__)

class BackupService:
    
    @staticmethod
    async def create_backup(db: AsyncSession, name: str, description: str = None) -> Dict[str, Any]:
        backup_data = {}
        
        # Backup Users
        result = await db.execute(select(User))
        users = result.scalars().all()
        backup_data['users'] = [
            {
                'id': user.id,
                'email': user.email,
                'role': user.role.value,
                'is_active': user.is_active,
                'assigned_venue_id': user.assigned_venue_id,
                'token_version': user.token_version
            }
            for user in users
        ]
        
        # Backup Venues
        result = await db.execute(select(Venue))
        venues = result.scalars().all()
        backup_data['venues'] = [
            {
                'id': venue.id,
                'name': venue.name,
                'address': venue.address,
                'city': venue.city,
                'state': venue.state,
                'country': venue.country,
                'postal_code': venue.postal_code,
                'description': venue.description
            }
            for venue in venues
        ]
        
        # Backup Rooms
        result = await db.execute(select(Room))
        rooms = result.scalars().all()
        backup_data['rooms'] = [
            {
                'id': room.id,
                'venue_id': room.venue_id,
                'name': room.name,
                'capacity': room.capacity,
                'rate_per_hour': room.rate_per_hour,
                'type': room.type,
                'amenities': room.amenities,
                'description': room.description
            }
            for room in rooms
        ]
        
        # Backup Addons
        result = await db.execute(select(Addon))
        addons = result.scalars().all()
        backup_data['addons'] = [
            {
                'id': addon.id,
                'venue_id': addon.venue_id,
                'room_id': addon.room_id,
                'name': addon.name,
                'description': addon.description,
                'price': addon.price
            }
            for addon in addons
        ]
        
        # Backup Bookings
        result = await db.execute(select(Booking))
        bookings = result.scalars().all()
        backup_data['bookings'] = [
            {
                'id': booking.id,
                'room_id': booking.room_id,
                'start_time': booking.start_time.isoformat() if booking.start_time else None,
                'end_time': booking.end_time.isoformat() if booking.end_time else None,
                'status': booking.status.value,
                'total_cost': booking.total_cost,
                'rescheduled': booking.rescheduled,
                'created_at': booking.created_at.isoformat() if booking.created_at else None,
                'updated_at': booking.updated_at.isoformat() if booking.updated_at else None
            }
            for booking in bookings
        ]
        
        # Backup Booking Customers
        result = await db.execute(select(BookingCustomer))
        booking_customers = result.scalars().all()
        backup_data['booking_customers'] = [
            {
                'id': bc.id,
                'booking_id': bc.booking_id,
                'user_id': bc.user_id,
                'first_name': bc.first_name,
                'last_name': bc.last_name,
                'address': bc.address,
                'phone': bc.phone
            }
            for bc in booking_customers
        ]
        
        # Backup Booking Addons
        result = await db.execute(select(BookingAddon))
        booking_addons = result.scalars().all()
        backup_data['booking_addons'] = [
            {
                'id': ba.id,
                'booking_id': ba.booking_id,
                'addon_id': ba.addon_id,
                'quantity': ba.quantity,
                'subtotal': ba.subtotal
            }
            for ba in booking_addons
        ]
        
        # Backup Reviews
        result = await db.execute(select(Review))
        reviews = result.scalars().all()
        backup_data['reviews'] = [
            {
                'id': review.id,
                'user_id': review.user_id,
                'room_id': review.room_id,
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.isoformat() if review.created_at else None
            }
            for review in reviews
        ]
        
        # Backup Queries
        result = await db.execute(select(Query))
        queries = result.scalars().all()
        backup_data['queries'] = [
            {
                'id': query.id,
                'user_id': query.user_id,
                'subject': query.subject,
                'message': query.message,
                'status': query.status.value,
                'created_at': query.created_at.isoformat() if query.created_at else None
            }
            for query in queries
        ]
        
        # Backup Reports
        result = await db.execute(select(Report))
        reports = result.scalars().all()
        backup_data['reports'] = [
            {
                'id': report.id,
                'title': report.title,
                'body': report.body,
                'created_at': report.created_at.isoformat() if report.created_at else None
            }
            for report in reports
        ]
        
        # Add metadata
        backup_data['metadata'] = {
            'backup_created_at': datetime.now(timezone.utc).isoformat(),
            'total_users': len(backup_data['users']),
            'total_venues': len(backup_data['venues']),
            'total_rooms': len(backup_data['rooms']),
            'total_bookings': len(backup_data['bookings']),
            'total_addons': len(backup_data['addons'])
        }
        
        return backup_data
    
    @staticmethod
    async def save_backup(db: AsyncSession, name: str, description: str = None) -> Backup:
        logger.info(f"Starting backup creation: {name}")
        backup_data = await BackupService.create_backup(db, name, description)
        logger.info(f"Backup data created with {len(backup_data.get('users', []))} users")
        
        # Upload to Vercel Blob
        vercel_info = {}
        try:
            logger.info(f"Uploading backup to Vercel Blob Storage: {name}")
            vercel_info = await VercelBlobService.upload_backup_to_vercel(backup_data, name)
            logger.info(f"Successfully uploaded backup to Vercel Blob: {vercel_info}")
        except Exception as e:
            # Log the error but don't fail the backup creation
            error_message = f"Vercel Blob upload failed: {str(e)}"
            logger.error(error_message, exc_info=True)
        
        # Create backup record
        backup = Backup(
            name=name,
            description=description,
            backup_data=backup_data,
            vercel_url=vercel_info.get("vercel_url") if vercel_info else None,
            vercel_pathname=vercel_info.get("vercel_pathname") if vercel_info else None,
            vercel_filename=vercel_info.get("filename") if vercel_info else None
        )
        
        logger.info(f"Saving backup to database with Vercel URL: {backup.vercel_url}")
        db.add(backup)
        await db.commit()
        await db.refresh(backup)
        
        logger.info(f"Backup saved successfully: ID={backup.id}, Vercel URL={backup.vercel_url}")
        return backup
    
    @staticmethod
    async def get_backup(db: AsyncSession, backup_id: int) -> Backup:
        result = await db.execute(select(Backup).where(Backup.id == backup_id))
        backup = result.scalar_one_or_none()
        return backup
    
    @staticmethod
    async def list_backups(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Backup]:
        result = await db.execute(
            select(Backup)
            .order_by(Backup.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def delete_backup(db: AsyncSession, backup_id: int) -> bool:
        result = await db.execute(select(Backup).where(Backup.id == backup_id))
        backup = result.scalar_one_or_none()
        
        if backup:
            await db.delete(backup)
            await db.commit()
            return True
        
        return False