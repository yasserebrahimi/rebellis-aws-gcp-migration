from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Rebellis Infrastructure"
    APP_VERSION: str = "1.0.0"
    APP_HOST: str = Field("0.0.0.0", env="APP_HOST")
    APP_PORT: int = Field(8000, env="APP_PORT")
    DEBUG: bool = Field(True, env="DEBUG")

    SECRET_KEY: str = Field(..., env="SECRET_KEY", description="Secret key for JWT tokens - MUST be set in production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    DATABASE_URL: str = Field("sqlite+aiosqlite:///./app.db", env="DATABASE_URL")
    DB_POOL_SIZE: int = Field(5, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(10, env="DB_MAX_OVERFLOW")

    REDIS_URL: str = Field("redis://localhost:6379", env="REDIS_URL")
    CACHE_TTL: int = Field(3600, env="CACHE_TTL")

    STORAGE_BACKEND: str = Field("local", env="STORAGE_BACKEND")
    GCS_BUCKET: str = Field("rebellis-uploads", env="GCS_BUCKET")
    UPLOAD_MAX_SIZE: int = Field(100 * 1024 * 1024, env="UPLOAD_MAX_SIZE")

    WHISPER_MODEL_PATH: str = Field("/models/whisper", env="WHISPER_MODEL_PATH")
    MOTION_MODEL_PATH: str = Field("/models/motion", env="MOTION_MODEL_PATH")
    TRITON_URL: str = Field("localhost:8001", env="TRITON_URL")

    CORS_ORIGINS: List[str] = Field(["http://localhost:3000"], env="CORS_ORIGINS")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = "json"
    ENABLE_METRICS: bool = Field(True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(9090, env="METRICS_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v
    
    @field_validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if not v or v == "dev-secret-key-change-me":
            raise ValueError("SECRET_KEY must be set to a secure value in production")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

settings = Settings()
