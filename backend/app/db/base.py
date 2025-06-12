# app/db/base.py

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models here so Alembic can detect them
from app.models.patient import Patient
from app.models.consultant import Consultant
from app.models.test import LabTest
from app.models.order import Order, OrderTest
from app.models.report import TestReport
from app.models.billing import Billing
from app.models.user import User
