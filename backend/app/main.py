from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import get_settings
from app.core.logging_conf import setup_logging
from app.api.routes import health, auth, users, venues, rooms, addons, bookings, favorites, reviews, queries, reports, search, cms

setup_logging()
settings = get_settings()

app = FastAPI(title="Hall Booking System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS if isinstance(settings.BACKEND_CORS_ORIGINS, list) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Centralized error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=400, content={"success": False, "error": {"code": "bad_request", "message": str(exc)}})

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(venues.router)
app.include_router(rooms.router)
app.include_router(addons.router)
app.include_router(bookings.router)
app.include_router(favorites.router)
app.include_router(reviews.router)
app.include_router(queries.router)
app.include_router(reports.router)
app.include_router(search.router)
app.include_router(cms.router)
app.include_router(health.router)
