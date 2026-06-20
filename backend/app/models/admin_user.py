"""AdminUser model — operator authentication with role support."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.models.base import Base


class AdminUser(Base):
    """Gym operator or Super Admin user."""

    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_temporary = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    # Added via _run_migrations — not created by create_all on existing DBs
    role = Column(String(20), nullable=False, default="admin")     # admin / super_admin
    gym_id = Column(Integer, nullable=True)                        # null for super_admin
