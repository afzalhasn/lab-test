# app/models/user.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Enum, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from app.core.config import settings
from enum import Enum as enum

class UserRole(str, enum):
    ADMIN = "ADMIN"
    LAB_ASSISTANT = "LAB_ASSISTANT"

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": settings.DB_SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    refresh_token = Column(Text, nullable=True)
    refresh_token_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
