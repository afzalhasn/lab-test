# app/api/routes/user.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from .schema import (
    UserCreate, UserLogin, UserOut, UserUpdate, UserProfile,
    TokenResponse, RefreshTokenResponse, PasswordChange, 
    RefreshTokenRequest, MessageResponse
)
from .crud import get_user_crud, UserCRUD
from app.core.auth import (
    create_access_token, create_refresh_token, decode_token, 
    get_current_user, get_current_active_user, require_admin,
    TokenType
)
from app.db.session import get_db
from app.core.config import settings
from app.models.user import UserRole

router = APIRouter(prefix=f"{settings.API_V1_STR}", tags=["Authentication"])

@router.post("/auth/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def signup(
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Create new user account"""
    user_crud = get_user_crud(db)
    
    # Check if username already exists
    existing_user = await user_crud.get_user_by_username(user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    try:
        user = await user_crud.create_user(user_in)
        input(user)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/auth/login", response_model=TokenResponse)
async def login(
    response: Response,
    user_in: UserLogin, 
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return access/refresh tokens"""
    user_crud = get_user_crud(db)
    
    # Authenticate user
    user = await user_crud.authenticate_user(user_in.username, user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create tokens
    token_data = {"sub": str(user.id), "username": user.username, "role": user.role.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Store refresh token in database
    await user_crud.store_refresh_token(user.id, refresh_token)
    
    # Set HTTP-only cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/auth/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    token_request: Optional[RefreshTokenRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    user_crud = get_user_crud(db)
    
    # Get refresh token from cookie or request body
    token = refresh_token or (token_request.refresh_token if token_request else None)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required"
        )
    
    # Validate refresh token
    try:
        payload = decode_token(token, TokenType.REFRESH)
        user_id = payload.get("sub")
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Get user and verify refresh token
    user = await user_crud.get_user_by_refresh_token(token)
    if not user or str(user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Create new access token
    token_data = {"sub": str(user.id), "username": user.username, "role": user.role.value}
    new_access_token = create_access_token(token_data)
    
    # Set new access token cookie
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE
    )
    
    return RefreshTokenResponse(
        access_token=new_access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/auth/logout", response_model=MessageResponse)
async def logout(
    response: Response,
    current_user: UserOut = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout user and revoke refresh token"""
    user_crud = get_user_crud(db)
    
    # Revoke refresh token
    await user_crud.revoke_refresh_token(current_user.id)
    
    # Clear cookies
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    
    return MessageResponse(message="Successfully logged out")

@router.get("/auth/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: UserOut = Depends(get_current_active_user)
):
    """Get current user profile"""
    return current_user

@router.put("/auth/me", response_model=UserProfile)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: UserOut = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile"""
    user_crud = get_user_crud(db)
    
    # Users can only update their own full_name, not role or is_active
    allowed_update = UserUpdate(full_name=user_update.full_name)
    
    updated_user = await user_crud.update_user(current_user.id, allowed_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user

@router.post("/auth/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: UserOut = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password"""
    user_crud = get_user_crud(db)
    
    # Verify current password
    user = await user_crud.authenticate_user(current_user.username, password_data.current_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    await user_crud.update_password(current_user.id, password_data.new_password)
    
    # Revoke refresh token to force re-login
    await user_crud.revoke_refresh_token(current_user.id)
    
    return MessageResponse(message="Password changed successfully")

# Admin-only endpoints
@router.get("/users", response_model=List[UserOut])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    role: Optional[UserRole] = None,
    _: UserOut = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get users list (Admin only)"""
    user_crud = get_user_crud(db)
    
    if role:
        users = await user_crud.get_users_by_role(role, is_active if is_active is not None else True)
    else:
        users = await user_crud.get_users(skip, limit, is_active)
    
    return users

@router.get("/users/{user_id}", response_model=UserOut)
async def get_user(
    user_id: UUID,
    _: UserOut = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID (Admin only)"""
    user_crud = get_user_crud(db)
    user = await user_crud.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/users/{user_id}", response_model=UserOut)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    _: UserOut = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update user (Admin only)"""
    user_crud = get_user_crud(db)
    
    updated_user = await user_crud.update_user(user_id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user

@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: UUID,
    hard_delete: bool = False,
    _: UserOut = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete or deactivate user (Admin only)"""
    user_crud = get_user_crud(db)
    
    if hard_delete:
        success = await user_crud.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return MessageResponse(message="User deleted successfully")
    else:
        user = await user_crud.deactivate_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return MessageResponse(message="User deactivated successfully")

@router.post("/users/{user_id}/activate", response_model=MessageResponse)
async def activate_user(
    user_id: UUID,
    _: UserOut = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Activate user (Admin only)"""
    user_crud = get_user_crud(db)
    
    user = await user_crud.activate_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return MessageResponse(message="User activated successfully")

