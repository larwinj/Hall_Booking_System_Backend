# app/middleware/json_logging.py
import logging
import os
import time
import uuid
from typing import Callable, Optional

import jwt  # pip install PyJWT
from pythonjsonlogger import jsonlogger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp
from logging.handlers import TimedRotatingFileHandler

# If you have a settings helper, import your secret/algorithms from there
from app.core.config import get_settings
SETTINGS = get_settings()
JWT_SECRET = getattr(SETTINGS, "JWT_SECRET", "change_me")
JWT_ALGS = getattr(SETTINGS, "JWT_ALGS", ["HS256"])


def _ensure_json_handlers(log_file: Optional[str]) -> None:
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    for h in root.handlers:
        if getattr(h, "_json_logger_inited", False):
            return

    fmt = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s "
        "%(request_id)s %(method)s %(path)s %(query)s %(status_code)s %(duration_ms)s "
        "%(client_ip)s %(user_agent)s %(user_id)s"
    )

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    console._json_logger_inited = True
    root.addHandler(console)

    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = TimedRotatingFileHandler(
            log_file, when="midnight", backupCount=7, encoding="utf-8", delay=True
        )
        file_handler.setFormatter(fmt)
        file_handler._json_logger_inited = True
        root.addHandler(file_handler)


def _extract_identity_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None, None, None

    # Some apps store "Bearer <jwt>" in the cookie, normalize it:
    if token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1].strip()

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGS)
        user_id = payload.get("sub") or payload.get("user_id")
        email = payload.get("email")
        role = payload.get("role")
        return user_id, email, role
    except Exception:
        return None, None, None


class JsonRequestResponseLogger(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, log_file: Optional[str] = "logs/app.jsonl"):
        super().__init__(app)
        _ensure_json_handlers(log_file)
        self.logger = logging.getLogger("app.request")

    async def dispatch(self, request: Request, call_next: Callable):
        start = time.perf_counter()
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        method = request.method
        path = request.url.path
        query = str(request.url.query or "")
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")

        user_id, user_email, user_role = _extract_identity_from_cookie(request)

        # Request log
        self.logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "query": query,
                "status_code": None,
                "duration_ms": None,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "user_id": user_id,
                # "user_email": user_email,
                # "user_role": user_role,
            },
        )

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "unhandled_exception",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "query": query,
                    "status_code": 500,
                    "duration_ms": duration_ms,
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                    "user_id": user_id,
                    "user_email": user_email,
                    "user_role": user_role,
                },
            )
            raise

        response.headers.setdefault("X-Request-ID", request_id)

        duration_ms = int((time.perf_counter() - start) * 1000)
        self.logger.info(
            "response",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "query": query,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "user_id": user_id,
                # "user_email": user_email,
                # "user_role": user_role,
            },
        )

        return response
