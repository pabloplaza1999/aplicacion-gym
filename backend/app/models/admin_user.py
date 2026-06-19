"""AdminUser model — single-row table for operator authentication."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.models.base import Base


class AdminUser(Base):
    """Single admin user for gym operator authentication."""

    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_temporary = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
