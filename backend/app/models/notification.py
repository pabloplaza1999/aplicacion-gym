"""Notification models — expiry alert log and SMTP settings."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from app.models.base import Base


class NotificationLog(Base):
    """Immutable record of each notification attempt (one row per membership+threshold+channel)."""

    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    membership_id = Column(Integer, ForeignKey("memberships.id", ondelete="SET NULL"), nullable=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="SET NULL"), nullable=True, index=True)
    threshold_days = Column(Integer, nullable=False)        # 7 | 3 | 1 | 0
    channel = Column(String(20), nullable=False, default="email")   # 'email' — Fase 3 adds others
    status = Column(String(10), nullable=False)             # 'sent' | 'failed'
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    recipient = Column(String(255), nullable=True)          # snapshot of address used; immutable


class NotificationSettings(Base):
    """Single-row SMTP configuration and threshold list. Always id=1; managed via upsert."""

    __tablename__ = "notification_settings"

    id = Column(Integer, primary_key=True)                  # always 1
    smtp_host = Column(String(255), nullable=True)
    smtp_port = Column(Integer, default=587)
    smtp_user = Column(String(255), nullable=True)
    smtp_password_encrypted = Column(Text, nullable=True)   # Fernet-encrypted; never plaintext
    smtp_from_name = Column(String(255), nullable=True)
    smtp_from_email = Column(String(255), nullable=True)
    thresholds = Column(String(100), default="[7,3,1,0]")  # JSON array of ints
    enabled = Column(Boolean, default=True, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)
