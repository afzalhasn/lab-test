# app/models/billing.py

import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, DateTime, Enum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.core.config import settings
import enum

class PaymentStatus(str, enum.Enum):
    PAID = "PAID"
    UNPAID = "UNPAID"
    PARTIAL = "PARTIAL"

class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    CARD = "CARD"
    UPI = "UPI"

class DiscountBy(str, enum.Enum):
    LAB = "LAB"
    DOCTOR = "DOCTOR"

class Billing(Base):
    __tablename__ = "billings"
    __table_args__ = {"schema": settings.DB_SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey(f"{settings.DB_SCHEMA}.orders.id"), nullable=False)

    total_amount = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    net_amount = Column(Numeric(10, 2), nullable=False)
    paid_amount = Column(Numeric(10, 2), default=0)
    due_amount = Column(Numeric(10, 2), default=0)
    discount_by = Column(Enum(DiscountBy), nullable=True)

    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.UNPAID)
    payment_method = Column(Enum(PaymentMethod), nullable=True)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="billing")
