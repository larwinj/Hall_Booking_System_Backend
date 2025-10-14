# Hall Booking System Backend (FastAPI)

Production-ready backend-only Hall Booking System.

## Stack & Features
- FastAPI (async)
- PostgreSQL (primary) via SQLAlchemy 2.0 (async) + Alembic
- MongoDB (CMS) via Motor
- JWT Auth (access + refresh) with bcrypt hashing
- Role-based access (customer, moderator, admin)
- Booking rules: conflict detection, total cost calculation, rescheduling, cancellation
- Search with fallback expansion
- Favorites, Reviews, Reports, Queries
- Docker + docker-compose (postgres, mongo, pgadmin, backend)
- Centralized error handling and structured logging
- Pytest samples

## Environment Variables
- POSTGRES_URL (e.g. postgresql+asyncpg://postgres:postgres@postgres:5432/hall_booking)
- POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD (for docker-compose postgres)
- MONGO_URI (e.g. mongodb://mongo:27017)
- JWT_SECRET, JWT_REFRESH_SECRET
- ACCESS_TOKEN_EXPIRE_MINUTES (default 30)
- REFRESH_TOKEN_EXPIRE_DAYS (default 7)
- ALGORITHM (default HS256)
- BACKEND_CORS_ORIGINS (default *)

Copy backend/.env.example to backend/.env and adjust if needed.

## Run with Docker
1) docker-compose up --build
2) Open Swagger at http://localhost:8000/docs

## Database
- Alembic is configured via backend/alembic. Initial migration provided at alembic/versions/0001_init.py
- The app creates tables according to models; enums and FKs are included.

## Seeding
Inside backend container:
- python scripts/seed.py
This seeds 3 users (admin, moderator, customer), 2 venues, 4 rooms, 3 addons, and a CMS page (Mongo).

Credentials:
- admin@example.com / Admin@123 (admin)
- mod@example.com / Mod@123 (moderator for Venue "City Center Hall")
- user@example.com / User@123 (customer)

## Testing
These sample tests assume the stack is running locally on http://localhost:8000
- pytest -q (from host) or run tests with your CI against the running docker-compose cluster.

Coverage:
- test_auth.py: signup, login, refresh
- test_rooms.py: list rooms
- test_booking.py: conflict detection

## API Overview
- Auth: /auth/signup, /auth/login, /auth/refresh, /auth/logout
- Users (admin): /users
- Venues: /venues (CRUD, admin)
- Rooms: /rooms (CRUD; moderators restricted to assigned_venue)
- Addons: /addons (CRUD, admin)
- Bookings: /bookings (create, reschedule, cancel, /bookings/me)
- Favorites: /favorites (customer only)
- Reviews: /reviews
- Queries: /queries (customer create; admin update/list)
- Reports: /reports (admin)
- Search: /search/rooms?city=&date=&capacity=&amenities=
- CMS (Mongo): /cms (CRUD), /cms/slug/{slug}

## Notes & Choices
- Refresh token revocation via user.token_version; logout increments version to invalidate prior refresh tokens.
- Booking conflict: overlaps if start < existing.end AND end > existing.start for same room and non-cancelled booking.
- Cost = ceil hours * room rate + sum(addon.price * qty). Subtotals stored per addon.
- Times are stored timezone-aware (UTC).
- CMS html_content sanitized with bleach before store/update.

## Sample curl
Signup:
curl -X POST "http://localhost:8000/auth/signup" -H "Content-Type: application/json" -d '{"email":"me@example.com","password":"Pass@123"}'

Login:
curl -X POST "http://localhost:8000/auth/login?email=me@example.com&password=Pass@123"

Search:
curl "http://localhost:8000/search/rooms?city=Metropolis&capacity=40&amenities=wifi&amenities=projector"

Create Booking:
curl -X POST "http://localhost:8000/bookings" -H "Authorization: Bearer $ACCESS" -H "Content-Type: application/json" -d '{"room_id":1,"start_time":"2030-01-01T10:00:00Z","end_time":"2030-01-01T12:00:00Z","addons":[{"addon_id":1,"quantity":2}]}'

Cancel:
curl -X POST "http://localhost:8000/bookings/1/cancel" -H "Authorization: Bearer $ACCESS" -H "Content-Type: application/json" -d '{"reason":"change of plans"}'

## Swagger/OpenAPI
Available at /docs after the stack is up.
