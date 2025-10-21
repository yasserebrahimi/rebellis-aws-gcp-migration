import time, logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from src.core.metrics import metrics

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        try:
            metrics.record_request(request.method, request.url.path, response.status_code, duration)
        except Exception:
            pass
        response.headers["X-Process-Time"] = str(duration)
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.client_requests = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        self.client_requests = {
            ip: [t for t in ts if t > now - 60] for ip, ts in self.client_requests.items()
        }
        ts = self.client_requests.get(client_ip, [])
        if len(ts) >= self.requests_per_minute:
            return Response(content="Rate limit exceeded", status_code=429, headers={"Retry-After": "60"})
        ts.append(now)
        self.client_requests[client_ip] = ts
        return await call_next(request)
