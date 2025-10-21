from pydantic import BaseModel
from typing import List
from datetime import datetime

class TranscriptionSegment(BaseModel):
    start: float
    end: float
    text: str
    confidence: float

class TranscriptionResponse(BaseModel):
    id: str
    text: str
    language: str
    segments: List[TranscriptionSegment]
    created_at: datetime

    class Config:
        from_attributes = True
