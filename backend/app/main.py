from os import read
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from app.core.config import get_settings
from app.core.logging_conf import setup_logging
from app.api.routes import health, auth, users, venues, rooms, addons, bookings, favorites, reviews, queries, reports, search, cms, analyticsreports, backup, wallet, booking_reports, meetings
from app.middleware.cors import setup_cors_middleware
# from app.middleware.security_headers import setup_security_headers_middleware
from app.middleware.rate_limiting import setup_rate_limiting_middleware
from app.middleware.trusted_hosts import setup_trusted_hosts_middleware
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
from typing import Callable

from app.middleware.json_logging import JsonRequestResponseLogger

# setup_logging()
settings = get_settings()
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        logger.info(f"Request: {request.method} {request.url} - Headers: {dict(request.headers)}")
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            logger.info(f"Response: {request.method} {request.url} - Status: {response.status_code} - Duration: {duration:.2f}s")
            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error: {request.method} {request.url} - Exception: {str(e)} - Duration: {duration:.2f}s")
            raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.db.session import init_db
    from app.db.mongo import get_client, close_client
    logger.info("Initializing database tables...")
    await init_db()
    logger.info("Database tables initialized.")
    
    app.state.mongo = get_client()
    yield
    logger.info("Application shutdown event triggered.")
    
    close_client()

app = FastAPI(title="Hall Booking System", version="1.0.0", lifespan=lifespan)


setup_trusted_hosts_middleware(app)
setup_rate_limiting_middleware(app)
setup_cors_middleware(app)
app.add_middleware(JsonRequestResponseLogger, log_file="logs/app.jsonl")
# setup_security_headers_middleware(app)
# app.add_middleware(LoggingMiddleware)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Exception: {str(exc)} - Request: {request.method} {request.url}")
    return JSONResponse(status_code=500, content={"success": False, "error": {"code": "internal_server_error", "message": "Internal server error"}})

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(venues.router)
app.include_router(rooms.router)
app.include_router(addons.router)
app.include_router(bookings.router)
app.include_router(booking_reports.router)
app.include_router(favorites.router)
app.include_router(reviews.router)
app.include_router(queries.router)
app.include_router(reports.router)
app.include_router(search.router)
app.include_router(cms.router)
app.include_router(analyticsreports.router)
app.include_router(backup.router)
app.include_router(wallet.router)
app.include_router(meetings.router)
app.include_router(health.router)