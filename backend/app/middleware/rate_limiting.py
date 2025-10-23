from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta
import time

class SimpleRateLimiter:
    """
    Simple in-memory rate limiter using a sliding window.
    Tracks requests per IP in the last window_seconds.
    """
    def __init__(self, requests_per_window: int = 100, window_seconds: int = 60):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)  

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        # Remove old requests outside the window
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip] if now - ts < self.window_seconds
        ]
        # Check if adding this request would exceed limit
        if len(self.requests[client_ip]) < self.requests_per_window:
            self.requests[client_ip].append(now)
            return True
        return False

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using IP address.
    Customize limits per route if needed by checking request.url.path.
    """
    def __init__(self, app, limiter: SimpleRateLimiter):
        super().__init__(app)
        self.limiter = limiter

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        if not self.limiter.is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Try again later.",
                headers={"Retry-After": "60"}
            )
        return await call_next(request)

# Global limiter instance (100 req/min per IP; adjust as needed)
GLOBAL_LIMITER = SimpleRateLimiter(requests_per_window=100, window_seconds=60)

def setup_rate_limiting_middleware(app):
    """
    Setup rate limiting middleware for the FastAPI app.
    """
    from fastapi import FastAPI
    app.add_middleware(RateLimitingMiddleware, limiter=GLOBAL_LIMITER)