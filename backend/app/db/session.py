from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from contextlib import asynccontextmanager, contextmanager
from app.db.dbconnection import db_manager

logger = logging.getLogger(__name__)

SessionLocal = async_sessionmaker(
    bind=db_manager.engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# For FastAPI Dependency
# @asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            await session.close()


# SessionLocalSync = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=db_manager.engine,
#     expire_on_commit=False
# )


# # For FastAPI Dependency
# def get_db_sync() -> Generator[Session, None, None]:
#     db = SessionLocalSync()
#     try:
#         yield db
#     finally:
#         db.close()


# # For background tasks / CLI scripts
# @contextmanager
# def get_db_context_sync() -> Generator[Session, None, None]:
#     session = SessionLocalSync()
#     try:
#         yield session
#         session.commit()
#     except SQLAlchemyError as e:
#         session.rollback()
#         logger.error(f"Database error: {str(e)}")
#         raise
#     finally:
#         session.close()
