from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from app.core.config import get_settings

_client: Optional[AsyncIOMotorClient] = None

def get_client() -> AsyncIOMotorClient:
    """Return the global motor client. Initialize lazily if needed."""
    global _client
    if _client is None:
        settings = get_settings()
        # Use newer Server API version and add connection options
        _client = AsyncIOMotorClient(
            settings.MONGO_URI,
            server_api=ServerApi('1'),
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000
        )
    return _client

def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
