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
        except Exception as e:
            logger.warning(f"Failed to record metrics: {e}")
        response.headers["X-Process-Time"] = str(duration)
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.client_requests = {}
        self.cleanup_interval = 300  # Clean up every 5 minutes
        self.last_cleanup = time.time()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Create a more unique identifier
        client_id = f"{client_ip}:{hash(user_agent) % 10000}"
        
        now = time.time()
        
        # Cleanup old entries periodically
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries(now)
            self.last_cleanup = now
        
        # Get or create request timestamps for this client
        ts = self.client_requests.get(client_id, [])
        
        # Remove timestamps older than 1 minute
        ts = [t for t in ts if t > now - 60]
        
        # Check rate limit
        if len(ts) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for client {client_ip}")
            return Response(
                content='{"error": "Rate limit exceeded", "retry_after": 60}',
                status_code=429,
                headers={"Retry-After": "60"},
                media_type="application/json"
            )
        
        # Add current request timestamp
        ts.append(now)
        self.client_requests[client_id] = ts
        
        return await call_next(request)
    
    def _cleanup_old_entries(self, now: float):
        """Clean up old entries to prevent memory leaks"""
        cutoff_time = now - 300  # Remove entries older than 5 minutes
        self.client_requests = {
            client_id: [t for t in ts if t > cutoff_time]
            for client_id, ts in self.client_requests.items()
            if any(t > cutoff_time for t in ts)
        }

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            logger.error(f"Middleware error: {exc}", exc_info=True)
            return Response(
                content='{"error": "Internal Server Error"}',
                status_code=500,
                media_type="application/json"
            )
