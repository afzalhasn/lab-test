from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from .crud import UserCRUD, get_user_crud
from .schema import UserCreate, UserUpdate, UserLogin, PasswordChange
from app.core.auth import create_access_token, create_refresh_token

class UserController:
    """Business logic layer for user operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_crud = get_user_crud(db)
        self.crud = UserCRUD(db)

    async def create_user(self, user_in):
        existing_user = await self.crud.get_user_by_username(user_in.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")

        user_in.password_hash = self.crud.hash_password(user_in.password)
        new_user = await self.crud.create_user(user_in)
        return new_user

    async def login(self, user_in):
        user = await self.crud.get_user_by_username(user_in.username)
        if not user or not self.crud.verify_password(user_in.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        access_token = self.crud.create_access_token(data={"sub": str(user.id), "username": user.username, "role": user.role})
        return {"access_token": access_token, "token_type": "bearer"}

def get_user_controller(db: AsyncSession) -> UserController:
    """Get UserController instance"""
    return UserController(db)

