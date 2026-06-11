"""Notification API routes — SMTP config, history, status, manual run."""

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

router = APIRouter(tags=["notifications"])


@router.get("/notifications/settings", response_model=NotificationSettingsRead)
def get_settings(db: Session = Depends(get_db)):
    return NotificationService(db).get_settings()


@router.put("/notifications/settings", response_model=NotificationSettingsRead)
def save_settings(data: NotificationSettingsUpdate, db: Session = Depends(get_db)):
    try:
        return NotificationService(db).save_settings(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/notifications/test-smtp")
def test_smtp(db: Session = Depends(get_db)):
    try:
        NotificationService(db).test_smtp()
        return {"message": "Correo de prueba enviado correctamente."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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
        raise HTTPException(status_code=500, detail=str(e))
