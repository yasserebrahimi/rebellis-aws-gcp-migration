from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies import get_db, get_current_user
from src.api.schemas.transcription import TranscriptionResponse
from src.services.transcription_service import TranscriptionService
from src.models.user import User

router = APIRouter()

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = "auto",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    svc = TranscriptionService(db)
    result = await svc.transcribe(audio_file=file, user_id=current_user.id, language=language)
    return result
