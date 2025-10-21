from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class MotionGenerationRequest(BaseModel):
    audio_path: str
    parameters: Optional[Dict[str, Any]] = None

class MotionGenerationResponse(BaseModel):
    id: str
    status: str
    motion_path: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
