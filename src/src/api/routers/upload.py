from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from src.api.dependencies import get_current_user
from src.api.schemas.upload import UploadResponse
from src.services.storage_service import StorageService
from src.models.user import User
from src.core.config import settings

router = APIRouter()

@router.post("/audio", response_model=UploadResponse)
async def upload_audio(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be audio/*")
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > settings.UPLOAD_MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    svc = StorageService()
    path = await svc.upload_uploadfile(file, f"users/{current_user.id}/audio/{file.filename}")
    return UploadResponse(file_id=file.filename, file_path=path, file_size=size, content_type=file.content_type)
