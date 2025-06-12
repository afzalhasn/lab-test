# app/models/user.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Enum, DateTime
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
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
