from pydantic import BaseModel, constr
from enum import Enum
from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import Field

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    LAB_ASSISTANT = "LAB_ASSISTANT"

# ----- Base Schemas -----

class UserBase(BaseModel):
    username: str
    full_name: str
    role: UserRole

# ----- Input Schemas -----

class UserCreate(BaseModel):
    username: str = Field(..., min_length=4, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: str
    role: UserRole

class UserLogin(BaseModel):
    username: str
    password: str

# ----- Output Schemas -----

class UserOut(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
