"""
Application Configuration Module
Comprehensive settings management with environment validation
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, SecretStr, PostgresDsn, RedisDsn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"


class Settings(BaseSettings):
    """Main application settings"""
    
    # ===== Application Info =====
    APP_NAME: str = "Rebellis Infrastructure"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-powered motion generation and speech transcription platform"
    APP_ENV: str = Field("development", env="APP_ENV")  # development, staging, production
    
    # ===== Server Configuration =====
    APP_HOST: str = Field("0.0.0.0", env="APP_HOST")
    APP_PORT: int = Field(8000, env="APP_PORT")
    WORKERS: int = Field(4, env="WORKERS")
    DEBUG: bool = Field(False, env="DEBUG")
    RELOAD: bool = Field(False, env="RELOAD")
    
    # ===== Security Settings =====
    SECRET_KEY: SecretStr = Field(..., env="SECRET_KEY")
    JWT_SECRET_KEY: SecretStr = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    PASSWORD_HASH_ROUNDS: int = Field(12, env="PASSWORD_HASH_ROUNDS")
    
    # OAuth Settings
    GOOGLE_CLIENT_ID: Optional[str] = Field(None, env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[SecretStr] = Field(None, env="GOOGLE_CLIENT_SECRET")
    GITHUB_CLIENT_ID: Optional[str] = Field(None, env="GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET: Optional[SecretStr] = Field(None, env="GITHUB_CLIENT_SECRET")
    
    # ===== Database Configuration =====
    DATABASE_URL: PostgresDsn = Field(..., env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(40, env="DATABASE_MAX_OVERFLOW")
    DATABASE_POOL_TIMEOUT: int = Field(30, env="DATABASE_POOL_TIMEOUT")
    DATABASE_POOL_RECYCLE: int = Field(3600, env="DATABASE_POOL_RECYCLE")
    DATABASE_ECHO: bool = Field(False, env="DATABASE_ECHO")
    
    # Test Database
    TEST_DATABASE_URL: Optional[PostgresDsn] = Field(None, env="TEST_DATABASE_URL")
    
    # ===== Redis Configuration =====
    REDIS_URL: RedisDsn = Field(..., env="REDIS_URL")
    REDIS_POOL_SIZE: int = Field(10, env="REDIS_POOL_SIZE")
    REDIS_DECODE_RESPONSES: bool = Field(True, env="REDIS_DECODE_RESPONSES")
    CACHE_TTL: int = Field(3600, env="CACHE_TTL")  # seconds
    SESSION_TTL: int = Field(86400, env="SESSION_TTL")  # 24 hours
    
    # ===== Storage Configuration =====
    STORAGE_BACKEND: str = Field("gcs", env="STORAGE_BACKEND")  # local, gcs, s3
    
    # GCS Settings
    GCS_PROJECT_ID: Optional[str] = Field(None, env="GCS_PROJECT_ID")
    GCS_BUCKET: Optional[str] = Field(None, env="GCS_BUCKET")
    GCS_CREDENTIALS_PATH: Optional[str] = Field(None, env="GCS_CREDENTIALS_PATH")
    GCS_PUBLIC_URL_BASE: Optional[str] = Field(None, env="GCS_PUBLIC_URL_BASE")
    
    # S3 Settings (for compatibility)
    S3_BUCKET: Optional[str] = Field(None, env="S3_BUCKET")
    S3_REGION: Optional[str] = Field(None, env="S3_REGION")
    S3_ACCESS_KEY_ID: Optional[SecretStr] = Field(None, env="S3_ACCESS_KEY_ID")
    S3_SECRET_ACCESS_KEY: Optional[SecretStr] = Field(None, env="S3_SECRET_ACCESS_KEY")
    
    # Local Storage
    LOCAL_STORAGE_PATH: Path = Field(DATA_DIR / "uploads", env="LOCAL_STORAGE_PATH")
    
    # Upload Settings
    UPLOAD_MAX_SIZE: int = Field(100 * 1024 * 1024, env="UPLOAD_MAX_SIZE")  # 100MB
    UPLOAD_ALLOWED_EXTENSIONS: List[str] = Field(
        [".mp3", ".wav", ".m4a", ".ogg", ".flac", ".mp4", ".avi", ".mov"],
        env="UPLOAD_ALLOWED_EXTENSIONS"
    )
    UPLOAD_CHUNK_SIZE: int = Field(1024 * 1024, env="UPLOAD_CHUNK_SIZE")  # 1MB
    
    # ===== ML Model Configuration =====
    # Model Paths
    WHISPER_MODEL_PATH: Path = Field(MODELS_DIR / "whisper", env="WHISPER_MODEL_PATH")
    MOTION_MODEL_PATH: Path = Field(MODELS_DIR / "motion", env="MOTION_MODEL_PATH")
    VAE_MODEL_PATH: Path = Field(MODELS_DIR / "vae", env="VAE_MODEL_PATH")
    
    # Model Settings
    WHISPER_MODEL_SIZE: str = Field("medium", env="WHISPER_MODEL_SIZE")  # tiny, base, small, medium, large
    WHISPER_DEVICE: str = Field("auto", env="WHISPER_DEVICE")  # auto, cuda, cpu
    WHISPER_COMPUTE_TYPE: str = Field("float16", env="WHISPER_COMPUTE_TYPE")
    WHISPER_BEAM_SIZE: int = Field(5, env="WHISPER_BEAM_SIZE")
    WHISPER_LANGUAGE: Optional[str] = Field(None, env="WHISPER_LANGUAGE")
    
    MOTION_MODEL_VERSION: str = Field("v1.5", env="MOTION_MODEL_VERSION")
    MOTION_DEVICE: str = Field("auto", env="MOTION_DEVICE")
    MOTION_BATCH_SIZE: int = Field(4, env="MOTION_BATCH_SIZE")
    MOTION_MAX_LENGTH: int = Field(600, env="MOTION_MAX_LENGTH")  # frames
    MOTION_FPS: int = Field(30, env="MOTION_FPS")
    MOTION_CACHE_TTL: int = Field(7200, env="MOTION_CACHE_TTL")  # 2 hours
    
    # Triton Settings
    TRITON_URL: Optional[str] = Field(None, env="TRITON_URL")
    TRITON_MODEL_VERSION: str = Field("-1", env="TRITON_MODEL_VERSION")  # latest
    TRITON_TIMEOUT: int = Field(60, env="TRITON_TIMEOUT")
    
    # ===== API Configuration =====
    API_V1_PREFIX: str = Field("/api/v1", env="API_V1_PREFIX")
    API_KEY_HEADER: str = Field("X-API-Key", env="API_KEY_HEADER")
    API_RATE_LIMIT: int = Field(100, env="API_RATE_LIMIT")  # requests per minute
    API_TIMEOUT: int = Field(30, env="API_TIMEOUT")  # seconds
    
    # CORS Settings
    CORS_ORIGINS: List[str] = Field(["http://localhost:3000"], env="CORS_ORIGINS")
    CORS_ALLOW_CREDENTIALS: bool = Field(True, env="CORS_ALLOW_CREDENTIALS")
    CORS_ALLOW_METHODS: List[str] = Field(["*"], env="CORS_ALLOW_METHODS")
    CORS_ALLOW_HEADERS: List[str] = Field(["*"], env="CORS_ALLOW_HEADERS")
    
    # ===== WebSocket Configuration =====
    WS_MESSAGE_QUEUE: str = Field("redis", env="WS_MESSAGE_QUEUE")  # redis, rabbitmq, kafka
    WS_HEARTBEAT_INTERVAL: int = Field(30, env="WS_HEARTBEAT_INTERVAL")
    WS_MAX_CONNECTIONS: int = Field(1000, env="WS_MAX_CONNECTIONS")
    WS_MAX_MESSAGE_SIZE: int = Field(1024 * 1024, env="WS_MAX_MESSAGE_SIZE")  # 1MB
    
    # ===== Queue Configuration =====
    CELERY_BROKER_URL: Optional[str] = Field(None, env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: Optional[str] = Field(None, env="CELERY_RESULT_BACKEND")
    TASK_MAX_RETRIES: int = Field(3, env="TASK_MAX_RETRIES")
    TASK_TIMEOUT: int = Field(300, env="TASK_TIMEOUT")  # 5 minutes
    
    # ===== Monitoring & Logging =====
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field("json", env="LOG_FORMAT")  # json, text
    LOG_FILE: Optional[Path] = Field(None, env="LOG_FILE")
    LOG_ROTATION: str = Field("100 MB", env="LOG_ROTATION")
    LOG_RETENTION: str = Field("30 days", env="LOG_RETENTION")
    
    # Metrics
    ENABLE_METRICS: bool = Field(True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(9090, env="METRICS_PORT")
    METRICS_PATH: str = Field("/metrics", env="METRICS_PATH")
    
    # Tracing
    ENABLE_TRACING: bool = Field(False, env="ENABLE_TRACING")
    JAEGER_HOST: Optional[str] = Field(None, env="JAEGER_HOST")
    JAEGER_PORT: Optional[int] = Field(None, env="JAEGER_PORT")
    
    # Sentry
    SENTRY_DSN: Optional[str] = Field(None, env="SENTRY_DSN")
    SENTRY_ENVIRONMENT: Optional[str] = Field(None, env="SENTRY_ENVIRONMENT")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(0.1, env="SENTRY_TRACES_SAMPLE_RATE")
    
    # ===== Feature Flags =====
    ENABLE_REGISTRATION: bool = Field(True, env="ENABLE_REGISTRATION")
    ENABLE_SOCIAL_AUTH: bool = Field(False, env="ENABLE_SOCIAL_AUTH")
    ENABLE_API_DOCS: bool = Field(True, env="ENABLE_API_DOCS")
    ENABLE_GRAPHQL: bool = Field(False, env="ENABLE_GRAPHQL")
    ENABLE_WEBSOCKET: bool = Field(True, env="ENABLE_WEBSOCKET")
    ENABLE_BATCH_PROCESSING: bool = Field(True, env="ENABLE_BATCH_PROCESSING")
    
    # ===== External Services =====
    SMTP_HOST: Optional[str] = Field(None, env="SMTP_HOST")
    SMTP_PORT: Optional[int] = Field(None, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[SecretStr] = Field(None, env="SMTP_PASSWORD")
    SMTP_FROM: Optional[str] = Field(None, env="SMTP_FROM")
    
    SLACK_WEBHOOK_URL: Optional[str] = Field(None, env="SLACK_WEBHOOK_URL")
    DISCORD_WEBHOOK_URL: Optional[str] = Field(None, env="DISCORD_WEBHOOK_URL")
    
    # ===== Performance Tuning =====
    MAX_CONCURRENT_REQUESTS: int = Field(100, env="MAX_CONCURRENT_REQUESTS")
    MAX_QUEUED_REQUESTS: int = Field(1000, env="MAX_QUEUED_REQUESTS")
    REQUEST_TIMEOUT: int = Field(60, env="REQUEST_TIMEOUT")
    KEEPALIVE_TIMEOUT: int = Field(5, env="KEEPALIVE_TIMEOUT")
    
    # Output paths
    OUTPUT_DIR: Path = Field(DATA_DIR / "outputs", env="OUTPUT_DIR")
    TEMP_DIR: Path = Field(DATA_DIR / "temp", env="TEMP_DIR")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v
    
    @field_validator("UPLOAD_ALLOWED_EXTENSIONS", mode="before")
    def parse_extensions(cls, v):
        if isinstance(v, str):
            return [e.strip() for e in v.split(",") if e.strip()]
        return v
    
    @field_validator("APP_ENV", mode="after")
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production", "testing"]
        if v not in allowed:
            raise ValueError(f"APP_ENV must be one of {allowed}")
        return v
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.APP_ENV == "production"
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.APP_ENV == "development"
    
    def is_testing(self) -> bool:
        """Check if running in test mode"""
        return self.APP_ENV == "testing"
    
    def get_database_url(self) -> str:
        """Get appropriate database URL based on environment"""
        if self.is_testing() and self.TEST_DATABASE_URL:
            return str(self.TEST_DATABASE_URL)
        return str(self.DATABASE_URL)
    
    def create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.LOCAL_STORAGE_PATH,
            self.OUTPUT_DIR,
            self.TEMP_DIR,
            LOGS_DIR,
            MODELS_DIR,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Create global settings instance
settings = get_settings()

# Create directories on import
settings.create_directories()
