# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.v1.api import reset_database
from app.v1.api.user import router as user_router
# from app.api.account import router as account_router
# from app.api.consultant import router as consultant_router
# from app.api.tests import router as test_router
# from app.api.patients import router as patients_router
# from app.api.orders import router as orders_router
# from app.api.bills import router as bills_router
# from app.api.registrations import router as registrations_router
# from app.api.reports import router as reports_router
from app.db.dbconnection import db_manager
from app.middleware.error_handler import error_handler_middleware

# Default settings if config module is not available
STATIC_DIR = "static"
ALLOWED_ORIGINS = ["*"]

try:
    from app.core.config import settings
    STATIC_DIR = settings.STATIC_DIR
    ALLOWED_ORIGINS = settings.ALLOWED_ORIGINS
except ImportError:
    pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Initialize database schema
        await db_manager.init_db()
        yield
    finally:
        # Cleanup on shutdown
        await db_manager.dispose()

def create_app() -> FastAPI:
    app = FastAPI(
        title="Diagnosis Application",
        description="Medical Diagnosis Application API Service",
        version="1.0",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add error handling middleware
    app.middleware("http")(error_handler_middleware)

    # Serve static files
    # app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # API Routers
    api_routers = [
        # account_router.router,
        # patients_router.router,
        # consultant_router.router,
        # test_router.router,
        # orders_router.router,
        # bills_router.router,
        # registrations_router.router,
        # reports_router.router,
        user_router.router,
        reset_database.router
    ]

    # Include all routers
    for router in api_routers:
        app.include_router(router)

    return app

app = create_app()
