"""Notification repository — log and settings persistence."""

import json
from datetime import datetime, time
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.membership import Membership
from app.models.notification import NotificationLog, NotificationSettings

_BOGOTA = ZoneInfo("America/Bogota")


class NotificationRepository:

    def __init__(self, db: Session):
        self.db = db

    # ── Settings (single-row, id=1) ──────────────────────────────────────────

    def get_settings(self) -> NotificationSettings:
        row = self.db.query(NotificationSettings).filter(NotificationSettings.id == 1).first()
        if row is None:
            # Column defaults are only applied on INSERT; set explicitly for in-memory objects
            row = NotificationSettings(
                id=1, enabled=True, smtp_port=587, thresholds="[7,3,1,0]"
            )
        return row

    def upsert_settings(self, **kwargs) -> NotificationSettings:
        row = self.db.query(NotificationSettings).filter(NotificationSettings.id == 1).first()
        if row is None:
            row = NotificationSettings(id=1, **kwargs)
            self.db.add(row)
        else:
            for k, v in kwargs.items():
                setattr(row, k, v)
            row.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(row)
        return row

    # ── Log operations ────────────────────────────────────────────────────────

    def get_sent_threshold_pairs(self, membership_ids: list[int]) -> set[tuple[int, int]]:
        """Single query — returns (membership_id, threshold_days) pairs already successfully sent.
        Used to deduplicate without N+1: caller loads all pairs once, checks in memory."""
        if not membership_ids:
            return set()
        rows = (
            self.db.query(NotificationLog.membership_id, NotificationLog.threshold_days)
            .filter(
                NotificationLog.membership_id.in_(membership_ids),
                NotificationLog.status == "sent",
                NotificationLog.channel == "email",
            )
            .all()
        )
        return {(r[0], r[1]) for r in rows}

    def log_attempt(
        self,
        membership_id: Optional[int],
        member_id: Optional[int],
        threshold_days: int,
        channel: str,
        status: str,
        error_message: Optional[str],
        recipient: Optional[str],
        sent_at: datetime,
    ) -> NotificationLog:
        log = NotificationLog(
            membership_id=membership_id,
            member_id=member_id,
            threshold_days=threshold_days,
            channel=channel,
            status=status,
            error_message=error_message,
            recipient=recipient,
            sent_at=sent_at,
        )
        self.db.add(log)
        self.db.commit()
        return log

    def bulk_update_last_notified(self, membership_ids: list[int], dt: datetime) -> None:
        if not membership_ids:
            return
        self.db.query(Membership).filter(Membership.id.in_(membership_ids)).update(
            {"last_notified_at": dt}, synchronize_session=False
        )
        self.db.commit()

    # ── History (paginated) ───────────────────────────────────────────────────

    def get_history(self, page: int = 1, page_size: int = 20) -> dict:
        page_size = min(page_size, 100)
        offset = (page - 1) * page_size

        total: int = self.db.execute(text("SELECT COUNT(*) FROM notification_logs")).scalar() or 0
        pages = max(1, -(-total // page_size))

        rows = self.db.execute(text("""
            SELECT nl.id, nl.membership_id, nl.member_id, nl.threshold_days, nl.channel,
                   nl.status, nl.error_message, nl.sent_at, nl.recipient,
                   m.full_name  AS member_name,
                   p.name       AS plan_name,
                   mb.end_date  AS end_date
            FROM notification_logs nl
            LEFT JOIN members     m  ON m.id  = nl.member_id
            LEFT JOIN memberships mb ON mb.id = nl.membership_id
            LEFT JOIN plans       p  ON p.id  = mb.plan_id
            ORDER BY nl.sent_at DESC
            LIMIT :lim OFFSET :off
        """), {"lim": page_size, "off": offset}).fetchall()

        items = [
            {
                "id": r[0],
                "membership_id": r[1],
                "member_id": r[2],
                "threshold_days": r[3],
                "channel": r[4],
                "status": r[5],
                "error_message": r[6],
                "sent_at": r[7],
                "recipient": r[8],
                "member_name": r[9],
                "plan_name": r[10],
                "end_date": str(r[11]) if r[11] else None,
            }
            for r in rows
        ]
        return {"items": items, "total": total, "page": page, "pages": pages}

    # ── Operational status ────────────────────────────────────────────────────

    def get_operational_status(self) -> dict:
        today_bogota = datetime.now(_BOGOTA).date()
        today_start_utc = (
            datetime.combine(today_bogota, time.min)
            .replace(tzinfo=_BOGOTA)
            .astimezone(ZoneInfo("UTC"))
            .replace(tzinfo=None)
        )

        last_run = self.db.execute(text("SELECT MAX(sent_at) FROM notification_logs")).scalar()
        sent_today: int = self.db.execute(
            text("SELECT COUNT(*) FROM notification_logs WHERE status='sent' AND sent_at >= :s"),
            {"s": today_start_utc},
        ).scalar() or 0
        failed_today: int = self.db.execute(
            text("SELECT COUNT(*) FROM notification_logs WHERE status='failed' AND sent_at >= :s"),
            {"s": today_start_utc},
        ).scalar() or 0

        # Memberships eligible for notification but member lacks email
        pending_count: int = self.db.execute(text("""
            SELECT COUNT(*) FROM memberships m
            JOIN plans   p   ON p.id   = m.plan_id
            JOIN members mbr ON mbr.id = m.member_id
            WHERE m.is_active = 1
              AND m.frozen_at IS NULL
              AND p.plan_type != 'voucher'
              AND m.end_date >= :now
              AND (mbr.email IS NULL OR mbr.email = '')
        """), {"now": datetime.utcnow()}).scalar() or 0

        cfg = self.get_settings()
        return {
            "is_configured": bool(cfg.smtp_host and cfg.smtp_user),
            "enabled": cfg.enabled,
            "last_run_at": last_run,
            "sent_today": sent_today,
            "failed_today": failed_today,
            "pending_count": pending_count,
        }

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def parse_thresholds(raw: Optional[str]) -> list[int]:
        try:
            return json.loads(raw or "[7,3,1,0]")
        except Exception:
            return [7, 3, 1, 0]

    @staticmethod
    def serialize_thresholds(thresholds: list[int]) -> str:
        return json.dumps(sorted(set(thresholds), reverse=True))
