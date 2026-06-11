"""Backup API routes."""

from fastapi import APIRouter, HTTPException

from app.schemas.backup import BackupFile, BackupListResponse, BackupStatus
from app.services.backup_service import BackupService

router = APIRouter(tags=["backup"])


@router.get("/backup/status", response_model=BackupStatus)
def get_backup_status():
    """Summary for Dashboard: last automatic backup + indicator."""
    try:
        return BackupService().get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backup/list", response_model=BackupListResponse)
def list_backups():
    """Full backup list grouped by type for the admin modal."""
    try:
        return BackupService().list_backups()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/backup/manual", response_model=BackupFile)
def create_manual_backup():
    """Create a manual backup immediately."""
    try:
        return BackupService().create_backup("manual")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
