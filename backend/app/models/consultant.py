import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from app.core.config import settings
from app.db.base import Base

class Consultant(Base):
    __tablename__ = "consultants"
    __table_args__ = {"schema": settings.DB_SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    contact_number = Column(String, nullable=False)
    hospital_affiliation = Column(String, nullable=True)
    address = Column(String, nullable=False)
