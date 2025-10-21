from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
import re

app = FastAPI(title="Rebellis API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

def extract_version_from_path(path: str):
    m = re.match(r"^/api/v(\d+)(/|$)", path)
    return m.group(1) if m else None

@app.middleware("http")
async def versioning_middleware(request: Request, call_next):
    request.state.api_version = extract_version_from_path(request.url.path)
    return await call_next(request)

# Metrics
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(app).expose(app, include_in_schema=False, endpoint="/metrics", should_gzip=True)
except Exception as e:
    import logging
    logging.getLogger("uvicorn.error").warning("Prometheus instrumentation disabled: %s", e)

from starlette_limiter import Limiter, RateLimitMiddleware
import os
try:
    from redis.asyncio import from_url as redis_from_url
    _redis = redis_from_url(os.getenv("REDIS_URL","redis://localhost:6379/0"))
    _limiter = Limiter(redis=_redis)
    app.add_middleware(RateLimitMiddleware, limiter=_limiter, global_limits=["100/minute"])
except Exception as _e:
    pass

