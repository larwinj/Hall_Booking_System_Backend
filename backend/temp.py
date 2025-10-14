import asyncio
from sqlalchemy import text
from app.db.session import engine

async def test_connection():
    async with engine.connect() as connection:
        try:
            result = await connection.execute(text("SELECT 1"))
            print("Connection successful! Result:", result.scalar())
        except Exception as e:
            print("Connection failed:", str(e))

if __name__ == "__main__":
    asyncio.run(test_connection())