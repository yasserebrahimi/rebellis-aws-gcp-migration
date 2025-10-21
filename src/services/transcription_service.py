import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from src.ml_serving.whisper_service import whisper_service
from src.api.schemas.transcription import TranscriptionResponse, TranscriptionSegment

class TranscriptionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def transcribe(self, audio_file: UploadFile, user_id: int, language: str = "auto") -> TranscriptionResponse:
        res = await whisper_service.transcribe(audio_file, language)
        return TranscriptionResponse(
            id=str(uuid.uuid4()),
            text=res["text"],
            language=res["language"],
            segments=[
                # empty for stub
            ],
            created_at=datetime.utcnow(),
        )
