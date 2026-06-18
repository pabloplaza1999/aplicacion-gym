"""Notification API routes — SMTP config, history, status, manual run."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.notification import (
    NotificationHistoryResponse,
    NotificationRunResult,
    NotificationSettingsRead,
    NotificationSettingsUpdate,
    NotificationStatusPanel,
)
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["notifications"])


@router.get("/notifications/settings", response_model=NotificationSettingsRead)
def get_settings(db: Session = Depends(get_db)):
    return NotificationService(db).get_settings()


@router.put("/notifications/settings", response_model=NotificationSettingsRead)
def save_settings(data: NotificationSettingsUpdate, db: Session = Depends(get_db)):
    try:
        return NotificationService(db).save_settings(data)
    except ValueError as e:
        # ValueError from notification_service is a controlled operator-facing message.
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error al guardar configuración de notificaciones: %s", e)
        raise HTTPException(status_code=500, detail="Error al guardar la configuración.")


@router.post("/notifications/test-smtp")
def test_smtp(db: Session = Depends(get_db)):
    try:
        NotificationService(db).test_smtp()
        return {"message": "Correo de prueba enviado correctamente."}
    except ValueError as e:
        # ValueError from crypto_service (invalid key) is a controlled message.
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # smtplib exceptions may expose server hostname or auth details.
        logger.error("Error en prueba SMTP: %s", e)
        raise HTTPException(status_code=400, detail="Error al enviar el correo de prueba. Verifique la configuración SMTP.")


@router.get("/notifications/status", response_model=NotificationStatusPanel)
def get_status(db: Session = Depends(get_db)):
    return NotificationService(db).get_status()


@router.get("/notifications/history", response_model=NotificationHistoryResponse)
def get_history(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    return NotificationService(db).get_history(page=page, page_size=page_size)


@router.post("/notifications/run", response_model=NotificationRunResult)
def run_now(db: Session = Depends(get_db)):
    try:
        return NotificationService(db).run_evaluation_cycle()
    except Exception as e:
        logger.error("Error en ciclo de notificaciones: %s", e)
        raise HTTPException(status_code=500, detail="Error al ejecutar el ciclo de notificaciones.")
