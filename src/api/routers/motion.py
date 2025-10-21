from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies import get_db, get_current_user
from src.api.schemas.motion import MotionGenerationRequest, MotionGenerationResponse
from src.services.motion_service import MotionService
from src.models.user import User

router = APIRouter()

@router.post("/generate", response_model=MotionGenerationResponse)
async def generate_motion(
    request: MotionGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    svc = MotionService(db)
    result = await svc.generate_motion(audio_path=request.audio_path, user_id=current_user.id, parameters=request.parameters)
    return result

@router.get("/{motion_id}", response_model=MotionGenerationResponse)
async def get_motion(
    motion_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    svc = MotionService(db)
    res = await svc.get_motion(motion_id)
    if not res:
        raise HTTPException(status_code=404, detail="Motion not found")
    return res
