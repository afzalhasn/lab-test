# app/api/routes/user.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from .schema import UserCreate, UserLogin, UserOut
from app.core.security import hash_password, verify_password
from app.core.auth import create_access_token
from app.db.session import get_db_context
from app.core.config import settings

router = APIRouter(prefix=f"{settings.API_V1_STR}", tags=["Users"])

@router.post("/signup", response_model=UserOut)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(get_db_context)):
    pass

@router.post("/login")
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db_context)):
    pass

