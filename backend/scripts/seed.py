import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import get_settings
from app.core.security import get_password_hash
from app.models.enums import UserRole
from app.models.user import User
from app.models.venue import Venue
from app.models.room import Room
from app.models.addon import Addon
from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.cms_sanitize import sanitize_html

async def run():
    settings = get_settings()
    engine = create_async_engine(settings.POSTGRES_URL)
    Session = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with Session() as db:  # type: AsyncSession
        # users
        admin = User(email="admin@example.com", hashed_password=get_password_hash("Admin@123"), role=UserRole.admin)
        moderator = User(email="mod@example.com", hashed_password=get_password_hash("Mod@123"), role=UserRole.moderator)
        customer = User(email="user@example.com", hashed_password=get_password_hash("User@123"), role=UserRole.customer)
        db.add_all([admin, moderator, customer])
        await db.flush()

        # venues
        v1 = Venue(name="City Center Hall", address="123 Main St", city="Metropolis", state="Metro", country="US", postal_code="10001", description="Central venue")
        v2 = Venue(name="Lakeside Pavilion", address="45 Lake Ave", city="Metropolis", state="Metro", country="US", postal_code="10002", description="By the lake")
        db.add_all([v1, v2])
        await db.flush()

        # assign moderator
        moderator.assigned_venue_id = v1.id

        # rooms
        rooms = [
            Room(venue_id=v1.id, name="Orchid", capacity=50, rate_per_hour=100.0, amenities=["projector","wifi"]),
            Room(venue_id=v1.id, name="Lotus", capacity=80, rate_per_hour=150.0, amenities=["stage","sound","wifi"]),
            Room(venue_id=v2.id, name="Maple", capacity=30, rate_per_hour=75.0, amenities=["wifi"]),
            Room(venue_id=v2.id, name="Cedar", capacity=120, rate_per_hour=220.0, amenities=["sound","projector","wifi"]),
        ]
        db.add_all(rooms)

        # addons
        addons = [
            Addon(name="Catering Basic", description="Snacks and drinks", price=10.0),
            Addon(name="Photography", description="Event photography", price=200.0),
            Addon(name="Decoration", description="Basic decor", price=150.0),
        ]
        db.add_all(addons)

        await db.commit()

    # CMS page
    mc = AsyncIOMotorClient(settings.MONGO_URI)
    col = mc.hall_cms.cms_pages
    await col.insert_one({
        "slug": "welcome",
        "title": "Welcome",
        "html_content": sanitize_html("<h1>Welcome</h1><p>Book your next event with us.</p>"),
        "metadata": {"hero":"welcome"},
        "attachments": [],
        "published": True,
    })

if __name__ == "__main__":
    asyncio.run(run())
