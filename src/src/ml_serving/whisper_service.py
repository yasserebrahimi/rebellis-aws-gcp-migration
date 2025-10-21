"""
Whisper Speech-to-Text Service
Complete implementation with multiple model sizes and optimization
"""

import asyncio
import logging
import tempfile
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from fastapi import UploadFile

import torch
import whisper
import numpy as np

from src.core.config import settings
from src.core.exceptions import MLModelError
from src.core.metrics import metrics
from src.core.cache import redis_client

logger = logging.getLogger(__name__)


class WhisperService:
    """Production-ready Whisper ASR service with caching and optimization"""
    
    def __init__(self, model_dir: str = None):
        self.model_dir = Path(model_dir or settings.WHISPER_MODEL_PATH)
        self.model = None
        self.device = None
        self.model_size = settings.WHISPER_MODEL_SIZE
        self.compute_type = settings.WHISPER_COMPUTE_TYPE
        self.cache_enabled = settings.WHISPER_CACHE_ENABLED
        self.cache_ttl = settings.WHISPER_CACHE_TTL
        
        # Performance settings
        self.batch_size = settings.WHISPER_BATCH_SIZE
        self.beam_size = settings.WHISPER_BEAM_SIZE
        self.temperature = settings.WHISPER_TEMPERATURE
        
    async def load_model(self):
        """Load Whisper model with GPU/CPU optimization"""
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            start_time = time.time()
            
            # Determine device
            if torch.cuda.is_available() and settings.USE_GPU:
                self.device = "cuda"
                logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
            else:
                self.device = "cpu"
                logger.info("Using CPU for inference")
            
            # Load model with appropriate size
            if settings.USE_FASTER_WHISPER:
                # Use faster-whisper for optimized inference
                from faster_whisper import WhisperModel
                self.model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type,
                    num_workers=settings.WHISPER_NUM_WORKERS,
                    download_root=str(self.model_dir)
                )
            else:
                # Use original OpenAI Whisper
                self.model = whisper.load_model(
                    self.model_size,
                    device=self.device,
                    download_root=str(self.model_dir)
                )
            
            load_time = time.time() - start_time
            logger.info(f"Whisper model loaded successfully in {load_time:.2f}s")
            metrics.record_model_load("whisper", "success", load_time)
            
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            metrics.record_model_load("whisper", "error", 0)
            raise MLModelError(f"Failed to load Whisper model: {e}", "whisper")
    
    async def transcribe(
        self,
        audio_file: UploadFile,
        language: Optional[str] = None,
        task: str = "transcribe",
        return_timestamps: bool = True,
        return_segments: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text
        
        Args:
            audio_file: Uploaded audio file
            language: Source language code (auto-detect if None)
            task: 'transcribe' or 'translate'
            return_timestamps: Include word-level timestamps
            return_segments: Include segment information
        
        Returns:
            Transcription results with text, segments, and metadata
        """
        if not self.model:
            raise MLModelError("Whisper model not loaded", "whisper")
        
        start_time = time.time()
        audio_hash = None
        
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                content = await audio_file.read()
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
            
            # Check cache if enabled
            if self.cache_enabled:
                import hashlib
                audio_hash = hashlib.sha256(content).hexdigest()
                cached_result = await redis_client.get(f"whisper:{audio_hash}")
                if cached_result:
                    logger.info(f"Cache hit for audio hash: {audio_hash}")
                    metrics.record_cache_hit("whisper")
                    return cached_result
            
            # Prepare options
            options = {
                "language": language,
                "task": task,
                "beam_size": self.beam_size,
                "temperature": self.temperature,
                "compression_ratio_threshold": 2.4,
                "no_speech_threshold": 0.6,
                "condition_on_previous_text": True,
                **kwargs
            }
            
            # Run transcription
            if settings.USE_FASTER_WHISPER:
                result = await self._transcribe_faster_whisper(tmp_file_path, options)
            else:
                result = await self._transcribe_openai_whisper(tmp_file_path, options)
            
            # Process result
            processed_result = {
                "text": result.get("text", "").strip(),
                "language": result.get("language", language),
                "task": task,
                "duration": result.get("duration", 0),
                "processing_time": time.time() - start_time
            }
            
            # Add segments if requested
            if return_segments and "segments" in result:
                processed_result["segments"] = [
                    {
                        "id": seg.get("id", i),
                        "start": seg.get("start", 0),
                        "end": seg.get("end", 0),
                        "text": seg.get("text", "").strip(),
                        "confidence": seg.get("confidence", seg.get("avg_logprob", 0))
                    }
                    for i, seg in enumerate(result["segments"])
                ]
            
            # Add word-level timestamps if available
            if return_timestamps and "words" in result:
                processed_result["words"] = result["words"]
            
            # Cache result if enabled
            if self.cache_enabled and audio_hash:
                await redis_client.set(
                    f"whisper:{audio_hash}",
                    processed_result,
                    ttl=self.cache_ttl
                )
                metrics.record_cache_miss("whisper")
            
            # Record metrics
            duration = time.time() - start_time
            metrics.record_inference("whisper", "success", duration)
            metrics.record_audio_processed(len(content), duration)
            
            logger.info(f"Transcription completed in {duration:.2f}s")
            return processed_result
            
        except Exception as e:
            duration = time.time() - start_time
            metrics.record_inference("whisper", "error", duration)
            logger.error(f"Transcription failed: {e}")
            raise MLModelError(f"Transcription failed: {str(e)}", "whisper")
            
        finally:
            # Cleanup temp file
            try:
                Path(tmp_file_path).unlink()
            except:
                pass
    
    async def _transcribe_openai_whisper(self, audio_path: str, options: dict) -> dict:
        """Transcribe using OpenAI Whisper"""
        loop = asyncio.get_event_loop()
        
        def _transcribe():
            return self.model.transcribe(audio_path, **options)
        
        result = await loop.run_in_executor(None, _transcribe)
        return result
    
    async def _transcribe_faster_whisper(self, audio_path: str, options: dict) -> dict:
        """Transcribe using faster-whisper"""
        loop = asyncio.get_event_loop()
        
        def _transcribe():
            segments, info = self.model.transcribe(audio_path, **options)
            return {
                "text": " ".join([s.text for s in segments]),
                "segments": [
                    {
                        "id": s.id,
                        "start": s.start,
                        "end": s.end,
                        "text": s.text,
                        "avg_logprob": s.avg_logprob
                    }
                    for s in segments
                ],
                "language": info.language,
                "duration": info.duration
            }
        
        result = await loop.run_in_executor(None, _transcribe)
        return result
    
    async def detect_language(self, audio_file: UploadFile) -> Dict[str, float]:
        """Detect language probabilities from audio"""
        if not self.model:
            raise MLModelError("Whisper model not loaded", "whisper")
        
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                content = await audio_file.read()
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
            
            # Load audio
            audio = whisper.load_audio(tmp_file_path)
            audio = whisper.pad_or_trim(audio)
            
            # Make log-Mel spectrogram
            mel = whisper.log_mel_spectrogram(audio).to(self.device)
            
            # Detect language
            _, probs = self.model.detect_language(mel)
            
            # Sort by probability
            sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
            
            return {
                "detected": sorted_probs[0][0],
                "confidence": sorted_probs[0][1],
                "probabilities": dict(sorted_probs[:10])
            }
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            raise MLModelError(f"Language detection failed: {str(e)}", "whisper")
        
        finally:
            try:
                Path(tmp_file_path).unlink()
            except:
                pass
    
    async def health_check(self) -> bool:
        """Check if service is healthy"""
        return self.model is not None
    
    def get_memory_usage(self) -> int:
        """Get estimated memory usage in bytes"""
        if not self.model:
            return 0
        
        # Estimate based on model size
        size_map = {
            "tiny": 39 * 1024 * 1024,      # 39 MB
            "base": 74 * 1024 * 1024,      # 74 MB
            "small": 244 * 1024 * 1024,    # 244 MB
            "medium": 769 * 1024 * 1024,   # 769 MB
            "large": 1550 * 1024 * 1024,   # 1550 MB
        }
        
        return size_map.get(self.model_size, 0)
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.model:
            del self.model
            self.model = None
            
            # Clear GPU cache if using CUDA
            if self.device == "cuda":
                torch.cuda.empty_cache()
            
            logger.info("Whisper model cleaned up")


# Singleton instance
whisper_service = WhisperService()
