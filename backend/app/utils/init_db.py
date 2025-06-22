"""Database initialization utilities"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_context
from app.models.user import User, UserRole
from app.core.security import hash_password
from app.v1.api.user.crud import UserCRUD
from app.v1.api.user.schema import UserCreate
import logging

logger = logging.getLogger(__name__)

async def create_default_admin():
    """Create default admin user if none exists"""
    async with get_db_context() as db:
        user_crud = UserCRUD(db)
        
        # Check if any admin user exists
        admin_users = await user_crud.get_users_by_role(UserRole.ADMIN)
        
        if not admin_users:
            try:
                # Create default admin user
                admin_data = UserCreate(
                    username="admin",
                    password="admin123",  # Change this in production!
                    full_name="System Administrator",
                    role=UserRole.ADMIN
                )
                
                admin_user = await user_crud.create_user(admin_data)
                logger.info(f"Default admin user created with ID: {admin_user.id}")
                logger.warning("⚠️  Default admin password is 'admin123' - CHANGE THIS IN PRODUCTION!")
                
            except Exception as e:
                logger.error(f"Failed to create default admin user: {str(e)}")
        else:
            logger.info("Admin user already exists, skipping creation")

async def init_database():
    """Initialize database with default data"""
    logger.info("Initializing database...")
    
    try:
        await create_default_admin()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(init_database()) 