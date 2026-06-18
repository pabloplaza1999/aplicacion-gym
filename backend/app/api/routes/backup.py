"""Backup API routes."""

import logging

from fastapi import APIRouter, HTTPException

from app.schemas.backup import BackupFile, BackupListResponse, BackupStatus
from app.services.backup_service import BackupService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["backup"])


@router.get("/backup/status", response_model=BackupStatus)
def get_backup_status():
    """Summary for Dashboard: last automatic backup + indicator."""
    try:
        return BackupService().get_status()
    except Exception as e:
        logger.error("Error al obtener estado del respaldo: %s", e)
        raise HTTPException(status_code=500, detail="Error al obtener el estado del respaldo.")


@router.get("/backup/list", response_model=BackupListResponse)
def list_backups():
    """Full backup list grouped by type for the admin modal."""
    try:
        return BackupService().list_backups()
    except Exception as e:
        logger.error("Error al listar respaldos: %s", e)
        raise HTTPException(status_code=500, detail="Error al listar los respaldos.")


@router.post("/backup/manual", response_model=BackupFile)
def create_manual_backup():
    """Create a manual backup immediately."""
    try:
        return BackupService().create_backup("manual")
    except Exception as e:
        logger.error("Error al crear respaldo manual: %s", e)
        raise HTTPException(status_code=500, detail="Error al crear el respaldo manual.")
