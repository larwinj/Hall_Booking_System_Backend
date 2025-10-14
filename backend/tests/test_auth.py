import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_signup_and_login(monkeypatch):
    # This test assumes running against a live backend+db via docker-compose.
    # In CI, you can spin containers before running tests.
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # signup
        r = await ac.post("/auth/signup", json={"email":"test1@example.com","password":"Test@123"})
        assert r.status_code in (200, 400)  # may already exist from previous run
        # login
        r2 = await ac.post("/auth/login", params={"email":"test1@example.com","password":"Test@123"})
        assert r2.status_code == 200
        data = r2.json()
        assert "access_token" in data and "refresh_token" in data

        # refresh
        r3 = await ac.post("/auth/refresh", params={"refresh_token": data["refresh_token"]})
        assert r3.status_code == 200
