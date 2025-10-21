"""
Motion Generation Service
Complete implementation for AI-driven motion synthesis
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from src.core.config import settings
from src.core.cache import redis_client
from src.core.exceptions import MotionGenerationError, NotFoundError
from src.core.metrics import metrics
from src.models.motion import Motion, MotionStatus
from src.storage.gcs import storage_client
from src.ml_serving.model_manager import model_manager

logger = logging.getLogger(__name__)


class MotionService:
    """Service for managing motion generation pipeline"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.storage = storage_client
        self.cache_ttl = settings.MOTION_CACHE_TTL
        
    async def generate_motion(
        self,
        audio_path: str,
        user_id: int,
        project_id: Optional[int] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate motion from audio
        
        Args:
            audio_path: Path to audio file in storage
            user_id: User ID for ownership
            project_id: Optional project association
            parameters: Motion generation parameters
        
        Returns:
            Motion generation job details
        """
        try:
            # Generate unique motion ID
            motion_id = str(uuid.uuid4())
            
            # Default parameters
            params = {
                "style": "natural",
                "energy": 1.0,
                "smoothness": 0.8,
                "fps": 30,
                "format": "bvh",
                "include_fingers": True,
                "include_face": False,
                **(parameters or {})
            }
            
            # Create motion record
            motion = Motion(
                id=motion_id,
                user_id=user_id,
                project_id=project_id,
                audio_path=audio_path,
                parameters=params,
                status=MotionStatus.PENDING,
                created_at=datetime.utcnow()
            )
            
            self.db.add(motion)
            await self.db.commit()
            
            # Publish background task
            asyncio.create_task(self._process_motion_job(motion_id))
            logger.info(f"Motion job {motion_id} created and queued")
            
            return {
                "id": motion_id,
                "status": motion.status.value,
                "created_at": motion.created_at,
                "parameters": params
            }
        except Exception as e:
            logger.error(f"Failed to create motion job: {e}", exc_info=True)
            raise MotionGenerationError(str(e))
    
    async def _process_motion_job(self, motion_id: str):
        """Process a motion generation job asynchronously"""
        try:
            # Fetch motion record
            query = select(Motion).where(Motion.id == motion_id)
            result = await self.db.execute(query)
            motion = result.scalar_one_or_none()
            
            if not motion:
                raise NotFoundError(f"Motion {motion_id} not found")
            
            # Update status
            motion.status = MotionStatus.PROCESSING
            motion.started_at = datetime.utcnow()
            await self.db.commit()
            
            # Run model inference
            model = await model_manager.get_model("motion_diffusion")
            audio_data = await self.storage.download(motion.audio_path)
            prediction = await model_manager.predict("motion_diffusion", audio_data, **motion.parameters)
            
            # Save generated file
            output_path = Path(settings.OUTPUT_DIR) / f"{motion_id}.bvh"
            output_path.write_text(prediction)
            cloud_path = await self.storage.upload(str(output_path), f"motions/{motion_id}.bvh")
            
            # Update final status
            motion.status = MotionStatus.COMPLETED
            motion.output_path = cloud_path
            motion.completed_at = datetime.utcnow()
            await self.db.commit()
            
            # Cache result
            await redis_client.set(f"motion:{motion_id}", cloud_path, ttl=self.cache_ttl)
            metrics.record_motion_job("success")
            logger.info(f"Motion job {motion_id} completed successfully")
        
        except Exception as e:
            logger.error(f"Motion job {motion_id} failed: {e}", exc_info=True)
            metrics.record_motion_job("error")
            
            # Update failure
            await self.db.execute(
                update(Motion)
                .where(Motion.id == motion_id)
                .values(status=MotionStatus.ERROR, error=str(e))
            )
            await self.db.commit()
    
    async def get_motion_status(self, motion_id: str) -> Dict[str, Any]:
        """Get job status and result if available"""
        query = select(Motion).options(selectinload(Motion.user)).where(Motion.id == motion_id)
        result = await self.db.execute(query)
        motion = result.scalar_one_or_none()
        
        if not motion:
            raise NotFoundError(f"Motion {motion_id} not found")
        
        return {
            "id": motion.id,
            "status": motion.status.value,
            "output_path": motion.output_path,
            "error": motion.error,
            "created_at": motion.created_at,
            "completed_at": motion.completed_at,
        }
