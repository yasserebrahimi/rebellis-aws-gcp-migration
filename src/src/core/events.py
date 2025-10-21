import logging
import asyncio
from fastapi import FastAPI

from src.core.config import settings
from src.ml_serving.model_manager import ModelManager
from src.core.cache import redis_client
from src.core.metrics import MetricsCollector

logger = logging.getLogger(__name__)

model_manager = ModelManager()
metrics = MetricsCollector()


async def startup_handler(app: FastAPI):
    """Initialize resources on application startup."""
    logger.info("🚀 Starting Rebellis application...")

    # Initialize Redis cache
    try:
        await redis_client.initialize()
        logger.info("✅ Redis connection established")
    except Exception as e:
        logger.error(f"⚠️ Failed to initialize Redis: {e}")

    # Load ML models asynchronously
    try:
        await model_manager.load_models()
        logger.info("✅ ML models loaded and ready")
    except Exception as e:
        logger.error(f"⚠️ Failed loading ML models: {e}")

    # Initialize metrics subsystem
    try:
        await metrics.start()
        logger.info("✅ Metrics collector initialized")
    except Exception as e:
        logger.warning(f"⚠️ Metrics disabled or failed: {e}")

    # Any async startup hooks (background tasks, queues, etc.)
    logger.info(f"App started in {settings.APP_ENV} mode (v{settings.APP_VERSION})")


async def shutdown_handler(app: FastAPI):
    """Cleanup resources on application shutdown."""
    logger.info("🛑 Shutting down Rebellis application...")

    try:
        await model_manager.cleanup()
        logger.info("🧹 Models cleaned up")
    except Exception as e:
        logger.error(f"Failed to cleanup models: {e}")

    try:
        await redis_client.close()
        logger.info("🔌 Redis connection closed")
    except Exception as e:
        logger.warning(f"Error during Redis closure: {e}")

    try:
        await metrics.stop()
        logger.info("📊 Metrics stopped gracefully")
    except Exception as e:
        logger.warning(f"Error stopping metrics: {e}")

    logger.info("✅ Application shutdown completed.")
