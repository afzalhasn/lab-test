import logging
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.db.base import Base

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self._engine: Optional[AsyncEngine] = None

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            self._engine = self._create_engine()
        return self._engine

    def _create_engine(self) -> AsyncEngine:
        return create_async_engine(
            settings.DATABASE_URL.replace("postgresql+psycopg2", "postgresql+asyncpg"),
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE,
            echo=settings.DB_ECHO,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    async def init_db(self) -> None:
        try:
            # Ensure the schema exists
            async with self.engine.begin() as conn:
                await conn.execute(
                    text(f'CREATE SCHEMA IF NOT EXISTS "{settings.DB_SCHEMA}"')
                )
                await conn.commit()

            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database initialized successfully")
        except SQLAlchemyError as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise

    async def dispose(self) -> None:
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            logger.info("Database connection disposed")

db_manager = DatabaseManager()
