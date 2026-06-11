"""Pydantic schemas for notification settings and history."""

from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class NotificationSettingsRead(BaseModel):
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_from_name: Optional[str] = None
    smtp_from_email: Optional[str] = None
    thresholds: List[int] = Field(default=[7, 3, 1, 0])
    enabled: bool = True
    is_configured: bool = False
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class NotificationSettingsUpdate(BaseModel):
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None       # plaintext — encrypted in service before storing
    smtp_from_name: Optional[str] = None
    smtp_from_email: Optional[str] = None
    thresholds: List[int] = Field(default=[7, 3, 1, 0])
    enabled: bool = True


class NotificationLogRead(BaseModel):
    id: int
    membership_id: Optional[int] = None
    member_id: Optional[int] = None
    member_name: Optional[str] = None
    plan_name: Optional[str] = None
    end_date: Optional[str] = None
    threshold_days: int
    channel: str
    status: str
    error_message: Optional[str] = None
    sent_at: datetime
    recipient: Optional[str] = None

    model_config = {"from_attributes": True}


class NotificationHistoryResponse(BaseModel):
    items: List[NotificationLogRead]
    total: int
    page: int
    pages: int


class NotificationStatusPanel(BaseModel):
    is_configured: bool
    enabled: bool
    last_run_at: Optional[datetime] = None
    sent_today: int = 0
    failed_today: int = 0
    pending_count: int = 0


class NotificationRunResult(BaseModel):
    sent: int
    skipped: int
    failed: int
    message: str
