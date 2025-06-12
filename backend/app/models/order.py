# app/models/order.py

import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, DateTime, Enum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.core.config import settings
import enum

class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class TestStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = {"schema": settings.DB_SCHEMA}


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey(f"{settings.DB_SCHEMA}.patients.id"), nullable=False)
    consultant_id = Column(UUID(as_uuid=True), ForeignKey(f"{settings.DB_SCHEMA}.consultants.id"), nullable=True)
    ordered_at = Column(DateTime, default=datetime.now)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    total_amount = Column(Numeric(10, 2), nullable=False)
    patient = relationship("Patient")
    consultant = relationship("Consultant")
    order_tests = relationship("OrderTest", back_populates="order")
    billing = relationship("Billing", uselist=False, back_populates="order")


class OrderTest(Base):
    __tablename__ = "order_tests"
    __table_args__ = {"schema": settings.DB_SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey(f"{settings.DB_SCHEMA}.orders.id"), nullable=False)
    test_id = Column(UUID(as_uuid=True), ForeignKey(f"{settings.DB_SCHEMA}.lab_tests.id"), nullable=False)
    status = Column(Enum(TestStatus), default=TestStatus.PENDING)
    sample_collected_at = Column(DateTime, nullable=True)

    order = relationship("Order", back_populates="order_tests")
    test = relationship("LabTest")
    report = relationship("TestReport", uselist=False, back_populates="order_test")
