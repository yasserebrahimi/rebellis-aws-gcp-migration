from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy import text
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections every hour
    pool_timeout=30,    # Timeout for getting connection from pool
    connect_args={
        "command_timeout": 60,
        "server_settings": {
            "application_name": settings.APP_NAME,
        }
    } if "postgresql" in settings.DATABASE_URL else {}
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class DatabaseManager:
    async def init_db(self):
        async with engine.begin() as conn:
            from src.models import user, project, task, ml_model  # noqa
            await conn.run_sync(Base.metadata.create_all)
            logger.info("DB tables ready")

    async def check_connection(self) -> bool:
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error("DB check failed: %s", e)
            return False

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

db_manager = DatabaseManager()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with db_manager.get_session() as s:
        yield s

async def init_db():
    await db_manager.init_db()
