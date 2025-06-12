from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from app.middleware.exceptions import BaseAPIException
import logging

logger = logging.getLogger(__name__)

async def error_handler_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except BaseAPIException as exc:
        # Log custom exceptions
        logger.error(f"API Error: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    except ValidationError as exc:
        # Handle Pydantic validation errors
        logger.error(f"Validation Error: {str(exc)}")
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()}
        )
    except SQLAlchemyError as exc:
        # Handle database errors
        logger.error(f"Database Error: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Database operation failed"}
        )
    except Exception as exc:
        # Handle unexpected errors
        logger.exception("Unexpected error occurred")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        ) 