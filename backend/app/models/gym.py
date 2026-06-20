"""Gym, GymLicense, and GymModule models — commercial licensing layer."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Text, UniqueConstraint
from app.models.base import Base


class Gym(Base):
    __tablename__ = "gyms"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    contact_name = Column(String(200), nullable=True)
    contact_email = Column(String(255), nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class GymLicense(Base):
    __tablename__ = "gym_licenses"

    id = Column(Integer, primary_key=True)
    gym_id = Column(Integer, ForeignKey("gyms.id"), nullable=False)
    plan_name = Column(String(50), nullable=False)     # starter / professional / premium
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=True)           # None = sin vencimiento
    status = Column(String(20), nullable=False, default="active")  # active/expired/suspended
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class GymModule(Base):
    __tablename__ = "gym_modules"

    id = Column(Integer, primary_key=True)
    gym_id = Column(Integer, ForeignKey("gyms.id"), nullable=False)
    module_key = Column(String(100), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    source = Column(String(20), nullable=False, default="addon")  # plan / addon
    activated_by = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    activated_at = Column(DateTime, nullable=True)
    deactivated_by = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    deactivated_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("gym_id", "module_key", name="uq_gym_modules_gym_module"),
    )
