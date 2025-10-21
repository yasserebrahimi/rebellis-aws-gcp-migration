from fastapi import FastAPI
from typing import Callable, Optional
from src.api.routers import (
    auth_router,
    health_router,
    motion_router,
    transcription_router,
    upload_router,
    websocket_router,
)
from src.core.config import settings

def create_app(lifespan: Optional[Callable] = None) -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Rebellis AI-Powered Motion Generation Infrastructure (skeleton)",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    app.include_router(health_router, prefix="/health", tags=["Health"])
    app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
    app.include_router(upload_router, prefix="/upload", tags=["Upload"])
    app.include_router(transcription_router, prefix="/transcription", tags=["Transcription"])
    app.include_router(motion_router, prefix="/motion", tags=["Motion"])
    app.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])
    return app
