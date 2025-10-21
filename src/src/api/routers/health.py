from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from sqlalchemy import text
from src.api.dependencies import get_db, get_redis

router = APIRouter()

@router.get("/")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy", "service": "rebellis-api"}

@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db), redis = Depends(get_redis)) -> Dict[str, Any]:
    db_ok = False
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    redis_ok = False
    try:
        if redis.redis_client:
            await redis.redis_client.ping()
            redis_ok = True
    except Exception:
        redis_ok = False
    return {"ready": db_ok and redis_ok, "checks": {"database": db_ok, "redis": redis_ok}}

@router.get("/live")
async def liveness_check() -> Dict[str, str]:
    return {"status": "alive"}
