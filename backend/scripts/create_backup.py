"""Standalone manual backup — stdlib only, no FastAPI dependency.

Usage (inside the backend container):
    python scripts/create_backup.py

Called by backup-manual.bat via:
    docker compose exec backend python scripts/create_backup.py
"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/app/data/gym.db")
BACKUP_DIR = Path("/app/data/backups/manual")
MAX_MANUAL = 10


def create_backup() -> None:
    if not DB_PATH.exists():
        print(f"[ERROR] No se encontro la base de datos en {DB_PATH}")
        raise SystemExit(1)

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"backup_manual_{ts}.db"

    src = sqlite3.connect(DB_PATH)
    dst = sqlite3.connect(dest)
    with dst:
        src.backup(dst)
    dst.close()
    src.close()

    # Retención: conservar los MAX_MANUAL más recientes
    files = sorted(BACKUP_DIR.glob("backup_manual_*.db"))
    while len(files) > MAX_MANUAL:
        oldest = files.pop(0)
        oldest.unlink()
        print(f"[INFO] Respaldo antiguo eliminado: {oldest.name}")

    print(f"[OK] Respaldo creado: {dest.name}")


if __name__ == "__main__":
    create_backup()
