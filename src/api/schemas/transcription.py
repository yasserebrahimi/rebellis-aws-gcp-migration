from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

class TranscriptionSegment(BaseModel):
    start: float = Field(..., ge=0, description="Start time in seconds")
    end: float = Field(..., ge=0, description="End time in seconds")
    text: str = Field(..., min_length=1, description="Transcribed text")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score between 0 and 1")

class TranscriptionRequest(BaseModel):
    language: str = Field("auto", description="Language code for transcription")
    return_timestamps: bool = Field(True, description="Include word-level timestamps")
    return_segments: bool = Field(True, description="Include segment information")
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v):
        if v != "auto" and len(v) != 2:
            raise ValueError('Language must be "auto" or a 2-letter language code')
        return v.lower()

class TranscriptionResponse(BaseModel):
    id: str
    text: str
    language: str
    segments: List[TranscriptionSegment]
    created_at: datetime
    processing_time: Optional[float] = None

    class Config:
        from_attributes = True
