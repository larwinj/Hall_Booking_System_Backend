import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_booking_conflict_detection(monkeypatch):
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # login seeded customer
        r = await ac.post("/auth/login", params={"email":"user@example.com","password":"User@123"})
        assert r.status_code == 200
        tokens = r.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        # find a room
        rooms = await ac.get("/rooms")
        room_id = rooms.json()[0]["id"]
        # create booking
        payload = {
            "room_id": room_id,
            "start_time": "2030-01-01T10:00:00Z",
            "end_time": "2030-01-01T12:00:00Z",
            "customer_ids": [],
            "addons": []
        }
        r1 = await ac.post("/bookings", json=payload, headers=headers)
        assert r1.status_code in (200, 409)
        # attempt overlapping booking
        r2 = await ac.post("/bookings", json=payload, headers=headers)
        if r1.status_code == 200:
            assert r2.status_code == 409
