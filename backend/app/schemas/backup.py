"""Backup schemas."""

from pydantic import BaseModel
from typing import List, Optional


class BackupFile(BaseModel):
    filename: str
    created_at: str   # ISO datetime string parsed from filename
    size_kb: float
    type: str         # 'automatic' | 'manual'


class BackupListResponse(BaseModel):
    automatic: List[BackupFile]
    manual: List[BackupFile]


class BackupStatus(BaseModel):
    last_backup: Optional[BackupFile] = None
    hours_ago: Optional[float] = None
    indicator: str = "red"   # 'green' (<24h) | 'orange' (24-48h) | 'red' (>48h or never)
