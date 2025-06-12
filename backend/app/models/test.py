import uuid
from sqlalchemy import Column, String, Numeric
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from app.core.config import settings


class LabTest(Base):
    __tablename__ = "lab_tests"
    __table_args__ = {"schema": settings.DB_SCHEMA}


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    cost = Column(Numeric(10, 2), nullable=False)
    sample_required = Column(String, nullable=True)
