from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi import Request
from app.core.config import get_settings

class TrustedHostsMiddleware(BaseHTTPMiddleware):
    """
    Restricts requests to trusted hosts only.
    Useful to prevent host header attacks.
    """
    def __init__(self, app, allowed_hosts: list):
        super().__init__(app)
        self.allowed_hosts = [host.lower() for host in allowed_hosts]

    async def dispatch(self, request: Request, call_next):
        host = request.headers.get("host", "").lower()
        if not any(allowed in host for allowed in self.allowed_hosts):
            return Response(
                status_code=400,
                content="Invalid host header",
                headers={"Content-Type": "text/plain"}
            )
        return await call_next(request)

def setup_trusted_hosts_middleware(app):
    """
    Setup trusted hosts middleware for the FastAPI app.
    """
    settings = get_settings()
    allowed_hosts = settings.ALLOWED_HOSTS if hasattr(settings, 'ALLOWED_HOSTS') else ["localhost", "127.0.0.1"]
    from fastapi import FastAPI
    app.add_middleware(TrustedHostsMiddleware, allowed_hosts=allowed_hosts)