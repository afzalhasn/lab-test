# app/api/reset_database.py
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.db.dbconnection import db_manager
from app.db.base import Base
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/admin",  # Changed prefix to include admin path
    tags=["Admin"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
    },
)

@router.delete(
    "/reset-database",
    status_code=status.HTTP_200_OK,
    description="Reset the entire database. WARNING: This will delete all data!",
    responses={
        status.HTTP_200_OK: {
            "description": "Database reset successful",
            "content": {
                "application/json": {
                    "example": {"message": "Database reset successful"}
                }
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error resetting database: <error details>"}
                }
            },
        },
    },
)
async def reset_database():
    """
    Reset the entire database by dropping all tables and recreating them.
    This operation is destructive and should only be used in development/testing.
    """
    if settings.ENV == "production":
        logger.error("Attempted to reset database in production environment")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Database reset not allowed in production environment"
        )

    try:
        logger.info("Starting database reset process")
        engine = db_manager.engine

        # Drop and recreate all tables using async run_sync
        async with engine.begin() as conn:
            logger.info("Dropping all tables")
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("Recreating all tables")
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database reset completed successfully")
        return {
            "message": "Database reset successful",
            "environment": settings.ENV
        }

    except SQLAlchemyError as e:
        error_msg = f"Database reset failed: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
    except Exception as e:
        error_msg = f"Unexpected error during database reset: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
