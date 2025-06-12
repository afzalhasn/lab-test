import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.core.config import settings
from app.db.base import Base

class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = {"schema": settings.DB_SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    age = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    contact_number = Column(String, nullable=False)
    address = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
