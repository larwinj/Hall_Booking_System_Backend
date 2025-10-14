import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_rooms_crud():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # list rooms (seeded)
        r = await ac.get("/rooms")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
