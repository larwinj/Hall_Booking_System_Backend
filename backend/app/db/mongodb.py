from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings

settings = get_settings()

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.MONGODB_DB_NAME]

bookings_collection = db["bookings_mirrored"]
reports_collection = db["monthly_reports"]