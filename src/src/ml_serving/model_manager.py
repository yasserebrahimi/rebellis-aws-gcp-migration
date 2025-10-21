"""
ML Model Manager
Centralized management for all machine learning models
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

import torch
from pydantic import BaseModel

from src.core.config import settings
from src.core.exceptions import MLModelError
from src.core.metrics import metrics
from src.core.cache import redis_client

logger = logging.getLogger(__name__)


class ModelStatus(str, Enum):
    """Model loading status"""
    NOT_LOADED = "not_loaded"
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"
    UNLOADING = "unloading"


class ModelType(str, Enum):
    """Supported model types"""
    WHISPER = "whisper"
    MOTION_DIFFUSION = "motion_diffusion"
    MOTION_VAE = "motion_vae"
    FACE_RECOGNITION = "face_recognition"
    GESTURE_CLASSIFIER = "gesture_classifier"


@dataclass
class ModelInfo:
    """Model information container"""
    name: str
    type: ModelType
    version: str
    path: Path
    device: str
    memory_usage: int
    status: ModelStatus
    load_time: float
    last_used: float
    error: Optional[str] = None


class ModelConfig(BaseModel):
    """Model configuration"""
    name: str
    type: ModelType
    version: str
    path: str
    device: str = "auto"
    enabled: bool = True
    preload: bool = False
    max_memory_mb: int = 2048
    timeout_seconds: int = 60
    cache_predictions: bool = True
    cache_ttl: int = 300


class ModelManager:
    """
    Centralized model lifecycle management
    Handles loading, caching, memory management, and cleanup
    """
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.model_info: Dict[str, ModelInfo] = {}
        self.model_configs: Dict[str, ModelConfig] = {}
        self._lock = asyncio.Lock()
        self._initialized = False
        
        # GPU management
        self.gpu_available = torch.cuda.is_available()
        self.gpu_count = torch.cuda.device_count() if self.gpu_available else 0
        
        # Memory limits
        self.max_gpu_memory = settings.MAX_GPU_MEMORY_MB * 1024 * 1024
        self.max_cpu_memory = settings.MAX_CPU_MEMORY_MB * 1024 * 1024
    
    async def initialize(self):
        """Initialize model manager and preload models"""
        if self._initialized:
            return
        
        async with self._lock:
            if self._initialized:
                return
            
            logger.info("Initializing Model Manager...")
            start_time = time.time()
            
            try:
                # Load model configurations
                await self._load_configurations()
                
                # Detect hardware capabilities
                await self._detect_hardware()
                
                # Preload enabled models
                preload_tasks = []
                for name, config in self.model_configs.items():
                    if config.enabled and config.preload:
                        preload_tasks.append(self.load_model(name))
                
                if preload_tasks:
                    results = await asyncio.gather(*preload_tasks, return_exceptions=True)
                    for idx, result in enumerate(results):
                        if isinstance(result, Exception):
                            model_name = list(self.model_configs.keys())[idx]
                            logger.error(f"Failed to preload model {model_name}: {result}")
                
                self._initialized = True
                init_time = time.time() - start_time
                logger.info(f"Model Manager initialized in {init_time:.2f}s")
                metrics.record_initialization("model_manager", init_time)
                
            except Exception as e:
                logger.error(f"Model Manager initialization failed: {e}")
                raise MLModelError(f"Initialization failed: {e}")
    
    async def _load_configurations(self):
        """Load model configurations from settings"""
        
        # Default configurations
        default_configs = [
            ModelConfig(
                name="whisper",
                type=ModelType.WHISPER,
                version=settings.WHISPER_MODEL_SIZE,
                path=settings.WHISPER_MODEL_PATH,
                device="cuda" if self.gpu_available else "cpu",
                enabled=settings.ENABLE_WHISPER,
                preload=settings.PRELOAD_WHISPER,
                max_memory_mb=2048,
                cache_predictions=True,
                cache_ttl=300
            ),
            ModelConfig(
                name="motion_diffusion",
                type=ModelType.MOTION_DIFFUSION,
                version="v1.0",
                path=settings.MOTION_MODEL_PATH,
                device="cuda" if self.gpu_available else "cpu",
                enabled=settings.ENABLE_MOTION_MODEL,
                preload=settings.PRELOAD_MOTION_MODEL,
                max_memory_mb=4096,
                cache_predictions=True,
                cache_ttl=600
            ),
            ModelConfig(
                name="motion_vae",
                type=ModelType.MOTION_VAE,
                version="v1.0",
                path=settings.MOTION_VAE_PATH,
                device="cuda" if self.gpu_available else "cpu",
                enabled=settings.ENABLE_MOTION_VAE,
                preload=False,
                max_memory_mb=1024,
                cache_predictions=True,
                cache_ttl=600
            )
        ]
        
        # Load configurations
        for config in default_configs:
            self.model_configs[config.name] = config
            self.model_info[config.name] = ModelInfo(
                name=config.name,
                type=config.type,
                version=config.version,
                path=Path(config.path),
                device=config.device,
                memory_usage=0,
                status=ModelStatus.NOT_LOADED,
                load_time=0,
                last_used=0
            )
    
    async def _detect_hardware(self):
        """Detect and log hardware capabilities"""
        logger.info("=" * 50)
        logger.info("Hardware Detection")
        logger
        # ... continuing from previous part

    async def _detect_hardware(self):
        """Detect and log hardware capabilities"""
        logger.info("=" * 50)
        logger.info("Hardware Detection")
        logger.info("=" * 50)
        
        # CPU info
        import psutil
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        logger.info(f"CPU Cores: {cpu_count}")
        logger.info(f"CPU Frequency: {cpu_freq.current:.2f} MHz")
        
        # Memory info
        memory = psutil.virtual_memory()
        logger.info(f"Total Memory: {memory.total / (1024**3):.2f} GB")
        logger.info(f"Available Memory: {memory.available / (1024**3):.2f} GB")
        
        # GPU info
        if self.gpu_available:
            for i in range(self.gpu_count):
                props = torch.cuda.get_device_properties(i)
                logger.info(f"GPU {i}: {props.name}")
                logger.info(f"  - Memory: {props.total_memory / (1024**3):.2f} GB")
                logger.info(f"  - Compute Capability: {props.major}.{props.minor}")
        else:
            logger.info("No GPU available, using CPU")
        
        logger.info("=" * 50)
    
    async def load_model(self, name: str) -> Any:
        """
        Load a model by name
        
        Args:
            name: Model name from configurations
            
        Returns:
            Loaded model instance
        """
        if name not in self.model_configs:
            raise MLModelError(f"Unknown model: {name}")
        
        if name in self.models and self.model_info[name].status == ModelStatus.READY:
            logger.debug(f"Model {name} already loaded")
            self.model_info[name].last_used = time.time()
            return self.models[name]
        
        async with self._lock:
            # Double-check after acquiring lock
            if name in self.models and self.model_info[name].status == ModelStatus.READY:
                return self.models[name]
            
            config = self.model_configs[name]
            info = self.model_info[name]
            
            logger.info(f"Loading model: {name} ({config.type.value})")
            info.status = ModelStatus.LOADING
            start_time = time.time()
            
            try:
                # Check memory availability
                await self._check_memory_availability(config)
                
                # Load model based on type
                if config.type == ModelType.WHISPER:
                    model = await self._load_whisper_model(config)
                elif config.type == ModelType.MOTION_DIFFUSION:
                    model = await self._load_motion_diffusion_model(config)
                elif config.type == ModelType.MOTION_VAE:
                    model = await self._load_motion_vae_model(config)
                else:
                    raise MLModelError(f"Unsupported model type: {config.type}")
                
                # Store model
                self.models[name] = model
                
                # Update info
                info.status = ModelStatus.READY
                info.load_time = time.time() - start_time
                info.last_used = time.time()
                info.memory_usage = await self._get_model_memory(model)
                
                logger.info(f"Model {name} loaded successfully in {info.load_time:.2f}s")
                logger.info(f"Memory usage: {info.memory_usage / (1024**2):.2f} MB")
                
                # Record metrics
                metrics.record_model_load(name, "success", info.load_time)
                metrics.gauge("model.memory.usage", info.memory_usage, tags={"model": name})
                
                return model
                
            except Exception as e:
                info.status = ModelStatus.ERROR
                info.error = str(e)
                logger.error(f"Failed to load model {name}: {e}")
                metrics.record_model_load(name, "error", 0)
                raise MLModelError(f"Failed to load model {name}: {e}")
    
    async def _check_memory_availability(self, config: ModelConfig):
        """Check if enough memory is available for model"""
        import psutil
        
        required_memory = config.max_memory_mb * 1024 * 1024
        
        if config.device.startswith("cuda"):
            # Check GPU memory
            if self.gpu_available:
                gpu_id = int(config.device.split(":")[-1]) if ":" in config.device else 0
                mem_free = torch.cuda.mem_get_info(gpu_id)[0]
                
                if mem_free < required_memory:
                    raise MLModelError(
                        f"Insufficient GPU memory. Required: {required_memory / (1024**2):.0f} MB, "
                        f"Available: {mem_free / (1024**2):.0f} MB"
                    )
        else:
            # Check CPU memory
            memory = psutil.virtual_memory()
            if memory.available < required_memory:
                raise MLModelError(
                    f"Insufficient CPU memory. Required: {required_memory / (1024**2):.0f} MB, "
                    f"Available: {memory.available / (1024**2):.0f} MB"
                )
    
    async def _load_whisper_model(self, config: ModelConfig):
        """Load Whisper ASR model"""
        from src.ml_serving.whisper_service import WhisperService
        
        service = WhisperService(model_dir=str(config.path))
        await service.load_model()
        return service
    
    async def _load_motion_diffusion_model(self, config: ModelConfig):
        """Load Motion Diffusion model"""
        # Import motion model implementation
        import torch
        from diffusers import DiffusionPipeline
        
        device = config.device if config.device != "auto" else ("cuda" if self.gpu_available else "cpu")
        
        # Load model from path or HuggingFace
        model = DiffusionPipeline.from_pretrained(
            str(config.path),
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            use_safetensors=True
        )
        
        model = model.to(device)
        
        # Enable optimizations
        if device == "cuda":
            model.enable_xformers_memory_efficient_attention()
        
        return model
    
    async def _load_motion_vae_model(self, config: ModelConfig):
        """Load Motion VAE model"""
        import torch
        from transformers import AutoModel
        
        device = config.device if config.device != "auto" else ("cuda" if self.gpu_available else "cpu")
        
        model = AutoModel.from_pretrained(
            str(config.path),
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            trust_remote_code=True
        )
        
        model = model.to(device)
        model.eval()
        
        return model
    
    async def _get_model_memory(self, model: Any) -> int:
        """Get model memory usage in bytes"""
        if hasattr(model, 'get_memory_usage'):
            return model.get_memory_usage()
        
        # Estimate based on parameters
        if hasattr(model, 'parameters'):
            param_size = sum(p.numel() * p.element_size() for p in model.parameters())
            buffer_size = sum(b.numel() * b.element_size() for b in model.buffers())
            return param_size + buffer_size
        
        # Default estimate
        return 100 * 1024 * 1024  # 100 MB
    
    async def unload_model(self, name: str):
        """Unload a model to free memory"""
        if name not in self.models:
            return
        
        async with self._lock:
            if name not in self.models:
                return
            
            logger.info(f"Unloading model: {name}")
            info = self.model_info[name]
            info.status = ModelStatus.UNLOADING
            
            try:
                model = self.models[name]
                
                # Call cleanup if available
                if hasattr(model, 'cleanup'):
                    await model.cleanup()
                
                # Delete model
                del self.models[name]
                
                # Clear GPU cache
                if info.device.startswith("cuda") and self.gpu_available:
                    torch.cuda.empty_cache()
                
                info.status = ModelStatus.NOT_LOADED
                info.memory_usage = 0
                
                logger.info(f"Model {name} unloaded successfully")
                metrics.record_model_unload(name, "success")
                
            except Exception as e:
                logger.error(f"Failed to unload model {name}: {e}")
                info.status = ModelStatus.ERROR
                info.error = str(e)
                metrics.record_model_unload(name, "error")
    
    async def get_model(self, name: str) -> Any:
        """Get a loaded model, loading it if necessary"""
        if name not in self.model_configs:
            raise MLModelError(f"Unknown model: {name}")
        
        if not self.model_configs[name].enabled:
            raise MLModelError(f"Model {name} is disabled")
        
        # Update last used time
        if name in self.models:
            self.model_info[name].last_used = time.time()
        
        # Load if not loaded
        if name not in self.models or self.model_info[name].status != ModelStatus.READY:
            await self.load_model(name)
        
        return self.models[name]
    
    async def predict(
        self,
        model_name: str,
        input_data: Any,
        **kwargs
    ) -> Any:
        """
        Run prediction with a model
        
        Args:
            model_name: Name of the model to use
            inpudata: Input data for prediction
            **kwargs: Additional prediction parameters
            
        Returns:
            Prediction result
        """
        # Check cache if enabled
        config = self.model_configs[model_name]
        cache_key = None
        
        if config.cache_predictions:
            import hashlib
            import pickle
            
            # Generate cache key
            cache_data = pickle.dumps((model_name, input_data, kwargs))
            cache_hash = hashlib.sha256(cache_data).hexdigest()
            cache_key = f"prediction:{model_name}:{cache_hash