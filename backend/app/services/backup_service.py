"""Backup service — filesystem + sqlite3 only, no SQLAlchemy."""

import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.core.config import settings
from app.schemas.backup import BackupFile, BackupListResponse, BackupStatus


class BackupService:

    def __init__(self) -> None:
        self._db_path = Path(settings.db_path)
        self._backup_dir = Path(settings.backup_dir)
        self._auto_dir = self._backup_dir / "automatic"
        self._manual_dir = self._backup_dir / "manual"

    # ── Public API ────────────────────────────────────────────────────────────

    def get_status(self) -> BackupStatus:
        """Return summary for Dashboard panel."""
        files = self._list_dir(self._auto_dir)
        if not files:
            return BackupStatus(indicator="red")
        latest = files[0]
        hours = self._hours_ago(latest.created_at)
        indicator = "green" if hours < 24 else ("orange" if hours < 48 else "red")
        return BackupStatus(last_backup=latest, hours_ago=round(hours, 1), indicator=indicator)

    def list_backups(self) -> BackupListResponse:
        """Return full list grouped by type for modal."""
        return BackupListResponse(
            automatic=self._list_dir(self._auto_dir),
            manual=self._list_dir(self._manual_dir),
        )

    def create_backup(self, backup_type: str) -> BackupFile:
        """Create a hot backup using sqlite3.backup(). backup_type: 'automatic' | 'manual'."""
        folder = self._auto_dir if backup_type == "automatic" else self._manual_dir
        folder.mkdir(parents=True, exist_ok=True)

        if backup_type == "automatic" and self._today_backup_exists(folder):
            files = self._list_dir(folder)
            return files[0]

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"gym_{timestamp}.db"
        dest = folder / filename

        src_conn = sqlite3.connect(str(self._db_path))
        dst_conn = sqlite3.connect(str(dest))
        try:
            src_conn.backup(dst_conn)
        finally:
            dst_conn.close()
            src_conn.close()

        max_count = settings.max_auto_backups if backup_type == "automatic" else settings.max_manual_backups
        self._apply_retention(folder, max_count)

        size_kb = dest.stat().st_size / 1024
        return BackupFile(
            filename=filename,
            created_at=self._filename_to_iso(filename),
            size_kb=round(size_kb, 1),
            type=backup_type,
        )

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _list_dir(self, folder: Path) -> List[BackupFile]:
        if not folder.exists():
            return []
        backup_type = folder.name  # 'automatic' or 'manual'
        files = sorted(
            [f for f in folder.iterdir() if f.suffix == ".db"],
            key=lambda f: f.name,
            reverse=True,
        )
        result = []
        for f in files:
            try:
                result.append(BackupFile(
                    filename=f.name,
                    created_at=self._filename_to_iso(f.name),
                    size_kb=round(f.stat().st_size / 1024, 1),
                    type=backup_type,
                ))
            except Exception:
                continue
        return result

    def _apply_retention(self, folder: Path, max_count: int) -> None:
        files = sorted(
            [f for f in folder.iterdir() if f.suffix == ".db"],
            key=lambda f: f.name,
        )
        while len(files) > max_count:
            files[0].unlink(missing_ok=True)
            files.pop(0)

    def _today_backup_exists(self, folder: Path) -> bool:
        today = datetime.now().strftime("%Y-%m-%d")
        return any(f.name.startswith(f"gym_{today}") for f in folder.glob("*.db"))

    @staticmethod
    def _filename_to_iso(filename: str) -> str:
        # gym_YYYY-MM-DD_HH-MM.db → YYYY-MM-DDTHH:MM:00
        try:
            stem = filename.replace("gym_", "").replace(".db", "")
            date_part, time_part = stem.split("_")
            hh, mm = time_part.split("-")
            return f"{date_part}T{hh}:{mm}:00"
        except Exception:
            return filename

    @staticmethod
    def _hours_ago(iso: str) -> float:
        try:
            dt = datetime.fromisoformat(iso)
            return (datetime.now() - dt).total_seconds() / 3600
        except Exception:
            return 9999
