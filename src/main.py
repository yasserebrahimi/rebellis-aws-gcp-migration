"""
Rebellis API Main Application Entry Point
Production-ready FastAPI application with complete middleware stack
"""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.sessions import SessionMiddleware

from src.api.middleware import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware,
    ErrorHandlingMiddleware
)
from src.api.routers import (
    auth,
    health,
    motion,
    transcription,
    upload,
    websocket,
    projects
)
from src.core.config import settings
from src.core.database import engine, Base
from src.core.events import startup_handler, shutdown_handler
from src.core.logging import setup_logging
from src.core.cache import redis_client
from src.ml_serving.model_manager import model_manager
from src.ml_serving.whisper_service import whisper_service

# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting Rebellis API...")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Initialize Redis cache
        logger.info("Connecting to Redis...")
        await redis_client.initialize()
        
        # Load ML models
        if settings.ENABLE_ML_MODELS:
            logger.info("Loading ML models...")
            await model_manager.initialize()
            
            # Load Whisper model
            if settings.ENABLE_WHISPER:
                await whisper_service.load_model()
        
        # Run custom startup handler
        await startup_handler(app)
        
        logger.info("Rebellis API started successfully")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        sys.exit(1)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Rebellis API...")
    
    try:
        # Run custom shutdown handler
        await shutdown_handler(app)
        
        # Cleanup ML models
        if settings.ENABLE_ML_MODELS:
            await model_manager.cleanup()
            
            if settings.ENABLE_WHISPER:
                await whisper_service.cleanup()
        
        # Close Redis connection
        await redis_client.close()
        
        # Close database connections
        await engine.dispose()
        
        logger.info("Rebellis API shutdown complete")
        
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    """
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Rebellis AI-Powered Motion Generation Platform",
        docs_url="/docs" if settings.ENABLE_DOCS else None,
        redoc_url="/redoc" if settings.ENABLE_DOCS else None,
        openapi_url="/openapi.json" if settings.ENABLE_DOCS else None,
        lifespan=lifespan
    )
    
    # Add middleware stack (order matters!)
    
    # 1. Error handling (outermost)
    app.add_middleware(ErrorHandlingMiddleware)
    
    # 2. CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time"]
    )
    
    # 3. Trusted Host
    if settings.ALLOWED_HOSTS:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS
        )
    
    # 4. Security Headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # 5. Session
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie=settings.SESSION_COOKIE_NAME,
        max_age=settings.SESSION_MAX_AGE,
        same_site="lax",
        https_only=settings.USE_HTTPS
    )
    
    # 6. GZip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # 7. Request Logging
    if settings.ENABLE_REQUEST_LOGGING:
        app.add_middleware(RequestLoggingMiddleware)
    
    # 8. Rate Limiting
    if settings.ENABLE_RATE_LIMITING:
        app.add_middleware(RateLimitMiddleware)
    
    # Add Prometheus metrics
    if settings.ENABLE_METRICS:
        instrumentator = Instrumentator(
            should_group_status_codes=False,
            should_ignore_untemplated=True,
            should_respect_env_var=True,
            should_instrument_requests_inprogress=True,
            excluded_handlers=[".*health.*", ".*metrics.*"],
            inprogress_name="http_requests_inprogress",
            inprogress_labels=True
        )
        instrumentator.instrument(app).expose(app, endpoint="/metrics")
    
    # Include routers
    app.include_router(health.router, prefix="/health", tags=["Health"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
    app.include_router(upload.router, prefix="/api/v1/upload", tags=["Upload"])
    app.include_router(transcription.router, prefix="/api/v1/transcribe", tags=["Transcription"])
    app.include_router(motion.router, prefix="/api/v1/motion", tags=["Motion"])
    app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
    
    # Root endpoint
    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "operational",
            "docs": "/docs" if settings.ENABLE_DOCS else None
        }
    
    # Custom error handlers
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "message": f"Path {request.url.path} not found",
                "path": request.url.path
            }
        )
    
    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc):
        logger.error(f"Internal error: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "request_id": request.state.request_id if hasattr(request.state, 'request_id') else None
            }
        )
    
    return app


# Create app instance
app = create_app()


def run():
    """
    Run the application using uvicorn
    """
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        loop="uvloop",
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.ENABLE_ACCESS_LOG,
        use_colors=True,
        reload=settings.DEBUG,
        ssl_keyfile=settings.SSL_KEY_FILE if settings.USE_HTTPS else None,
        ssl_certfile=settings.SSL_CERT_FILE if settings.USE_HTTPS else None,
        ssl_keyfile_password=settings.SSL_KEY_PASSWORD if settings.USE_HTTPS else None,
        ssl_version=settings.SSL_VERSION if settings.USE_HTTPS else None,
        ssl_cert_reqs=settings.SSL_CERT_REQS if settings.USE_HTTPS else None,
        ssl_ca_certs=settings.SSL_CA_CERTS if settings.USE_HTTPS else None,
        ssl_ciphers=settings.SSL_CIPHERS if settings.USE_HTTPS else None,
        limit_concurrency=settings.MAX_CONNECTIONS,
        limit_max_requests=settings.MAX_REQUESTS,
        timeout_keep_alive=settings.KEEP_ALIVE_TIMEOUT,
        server_header=False,
        date_header=False
    )


if __name__ == "__main__":
    run()
