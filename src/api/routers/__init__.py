from .auth import router as auth_router
from .health import router as health_router
from .motion import router as motion_router
from .transcription import router as transcription_router
from .upload import router as upload_router
from .websocket import router as websocket_router
__all__ = ["auth_router","health_router","motion_router","transcription_router","upload_router","websocket_router"]
