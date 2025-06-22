from pydantic import BaseModel, Field, EmailStr
from enum import Enum
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    LAB_ASSISTANT = "LAB_ASSISTANT"

# ----- Base Schemas -----

class UserBase(BaseModel):
    username: str = Field(..., min_length=4, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: UserRole

# ----- Input Schemas -----

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserLogin(BaseModel):
    username: str = Field(..., min_length=4, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)

class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=6, max_length=128)
    new_password: str = Field(..., min_length=6, max_length=128)

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# ----- Output Schemas -----

class UserOut(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserProfile(UserOut):
    """Extended user profile with additional info"""
    pass

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class MessageResponse(BaseModel):
    message: str
