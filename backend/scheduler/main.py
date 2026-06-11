"""Scheduler service — runs as a separate Docker container."""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from apscheduler.schedulers.blocking import BlockingScheduler
from app.database.session import SessionLocal
from app.services.backup_service import BackupService
from app.services.notification_service import NotificationService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [scheduler] %(message)s")
logger = logging.getLogger(__name__)


def run_automatic_backup() -> None:
    try:
        file = BackupService().create_backup("automatic")
        logger.info("Backup automático creado: %s (%.1f KB)", file.filename, file.size_kb)
    except Exception as e:
        logger.error("Error en backup automático: %s", e)


def run_notification_job() -> None:
    db = SessionLocal()
    try:
        result = NotificationService(db).run_evaluation_cycle()
        logger.info("Notificaciones: %s", result.message)
    except Exception as e:
        logger.error("Error en job de notificaciones: %s", e)
    finally:
        db.close()


def main() -> None:
    # Run backup immediately on startup if no backup exists for today
    svc = BackupService()
    status = svc.get_status()
    if status.last_backup is None or (status.hours_ago is not None and status.hours_ago >= 23):
        logger.info("Ejecutando backup inicial al arrancar...")
        run_automatic_backup()

    scheduler = BlockingScheduler(timezone="America/Bogota")
    scheduler.add_job(run_automatic_backup, "cron", hour=2, minute=0)
    scheduler.add_job(run_notification_job, "cron", hour=8, minute=0)
    logger.info("Scheduler iniciado — backup 02:00 AM · notificaciones 08:00 AM (America/Bogota)")
    scheduler.start()


if __name__ == "__main__":
    main()
