# app/models/test_report.py

import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.core.config import settings

class TestReport(Base):
    __tablename__ = "test_reports"
    __table_args__ = {"schema": settings.DB_SCHEMA}


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_test_id = Column(UUID(as_uuid=True), ForeignKey(f"{settings.DB_SCHEMA}.order_tests.id"), nullable=False)
    result = Column(JSONB, nullable=False)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    order_test = relationship("OrderTest", back_populates="report")

