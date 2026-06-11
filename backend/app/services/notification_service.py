"""Notification service — evaluates expiring memberships and dispatches email alerts."""

from datetime import datetime, timedelta, time
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.models.member import Member
from app.models.membership import Membership
from app.models.plan import Plan
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import (
    NotificationHistoryResponse,
    NotificationLogRead,
    NotificationRunResult,
    NotificationSettingsRead,
    NotificationSettingsUpdate,
    NotificationStatusPanel,
)
from app.services.crypto_service import encrypt
from app.services.email_service import EmailService

_BOGOTA = ZoneInfo("America/Bogota")
_UTC = ZoneInfo("UTC")

_THRESHOLD_LABEL = {0: "vence hoy", 1: "vence mañana"}


def _threshold_label(days: int) -> str:
    return _THRESHOLD_LABEL.get(days, f"vence en {days} días")


def _build_email(member_name: str, plan_name: str, end_date: datetime, threshold_days: int) -> tuple[str, str]:
    end_str = end_date.strftime("%d/%m/%Y")
    label = _threshold_label(threshold_days)
    subject = f"Tu membresía {label} — Rhino Power"
    body = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:24px;color:#333">
      <h2 style="color:#E02020;margin-bottom:8px">Aviso de vencimiento</h2>
      <p>Hola <strong>{member_name}</strong>,</p>
      <p>Tu membresía <strong>{plan_name}</strong> <strong>{label}</strong>.</p>
      <p>Fecha de vencimiento: <strong>{end_str}</strong></p>
      <p>Visítanos para renovar y continuar disfrutando de nuestras instalaciones.</p>
      <hr style="border:none;border-top:1px solid #eee;margin:20px 0"/>
      <p style="font-size:12px;color:#999">Este es un mensaje automático — no responder.</p>
    </div>
    """
    return subject, body


class NotificationService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = NotificationRepository(db)
        self.email_svc = EmailService()

    # ── Settings ──────────────────────────────────────────────────────────────

    def get_settings(self) -> NotificationSettingsRead:
        cfg = self.repo.get_settings()
        thresholds = NotificationRepository.parse_thresholds(cfg.thresholds)
        return NotificationSettingsRead(
            smtp_host=cfg.smtp_host,
            smtp_port=cfg.smtp_port or 587,
            smtp_user=cfg.smtp_user,
            smtp_from_name=cfg.smtp_from_name,
            smtp_from_email=cfg.smtp_from_email,
            thresholds=thresholds,
            enabled=cfg.enabled,
            is_configured=bool(cfg.smtp_host and cfg.smtp_user),
            updated_at=cfg.updated_at,
        )

    def save_settings(self, data: NotificationSettingsUpdate) -> NotificationSettingsRead:
        kwargs: dict = {
            "smtp_host": data.smtp_host,
            "smtp_port": data.smtp_port,
            "smtp_user": data.smtp_user,
            "smtp_from_name": data.smtp_from_name,
            "smtp_from_email": data.smtp_from_email,
            "thresholds": NotificationRepository.serialize_thresholds(data.thresholds),
            "enabled": data.enabled,
        }
        if data.smtp_password:
            kwargs["smtp_password_encrypted"] = encrypt(data.smtp_password)
        self.repo.upsert_settings(**kwargs)
        return self.get_settings()

    def test_smtp(self) -> None:
        cfg = self.repo.get_settings()
        if not cfg.smtp_host or not cfg.smtp_user or not cfg.smtp_password_encrypted:
            raise ValueError("SMTP no está completamente configurado.")
        self.email_svc.send_test(
            smtp_host=cfg.smtp_host,
            smtp_port=cfg.smtp_port or 587,
            smtp_user=cfg.smtp_user,
            smtp_password_encrypted=cfg.smtp_password_encrypted,
            from_name=cfg.smtp_from_name or "Gym",
            from_email=cfg.smtp_from_email or cfg.smtp_user,
        )

    # ── Evaluation cycle ──────────────────────────────────────────────────────

    def run_evaluation_cycle(self) -> NotificationRunResult:
        cfg = self.repo.get_settings()

        if not cfg.enabled:
            return NotificationRunResult(sent=0, skipped=0, failed=0, message="Notificaciones desactivadas.")
        if not cfg.smtp_host or not cfg.smtp_user or not cfg.smtp_password_encrypted:
            return NotificationRunResult(sent=0, skipped=0, failed=0, message="SMTP no configurado.")

        thresholds = NotificationRepository.parse_thresholds(cfg.thresholds)
        if not thresholds:
            return NotificationRunResult(sent=0, skipped=0, failed=0, message="Sin umbrales configurados.")

        # Compute UTC bounds for each threshold (Bogota-aware)
        today_bogota = datetime.now(_BOGOTA).date()
        threshold_windows: dict[int, tuple[datetime, datetime]] = {}
        for t in thresholds:
            target = today_bogota + timedelta(days=t)
            start = datetime.combine(target, time.min).replace(tzinfo=_BOGOTA).astimezone(_UTC).replace(tzinfo=None)
            threshold_windows[t] = (start, start + timedelta(days=1))

        min_start = min(w[0] for w in threshold_windows.values())
        max_end = max(w[1] for w in threshold_windows.values())

        # ── Single query: all eligible candidates across all thresholds ──────
        candidates = (
            self.db.query(Membership, Member, Plan)
            .join(Member, Member.id == Membership.member_id)
            .join(Plan, Plan.id == Membership.plan_id)
            .filter(
                Membership.is_active == True,           # noqa: E712
                Membership.frozen_at == None,           # noqa: E711  (excluir congeladas)
                Plan.plan_type != "voucher",            # excluir valeras
                Member.email != None,                   # noqa: E711  (solo con email)
                Member.email != "",
                Membership.end_date >= min_start,
                Membership.end_date < max_end,
            )
            .all()
        )

        if not candidates:
            return NotificationRunResult(sent=0, skipped=0, failed=0, message="Sin membresías por notificar hoy.")

        # ── Single query: all already-sent pairs (anti-N+1 deduplication) ────
        candidate_ids = [m.id for m, _, _ in candidates]
        sent_pairs = self.repo.get_sent_threshold_pairs(candidate_ids)

        sent = skipped = failed = 0
        now = datetime.utcnow()
        notified_membership_ids: list[int] = []

        for membership, member, plan in candidates:
            for t, (win_start, win_end) in threshold_windows.items():
                if not (win_start <= membership.end_date < win_end):
                    continue
                if (membership.id, t) in sent_pairs:
                    skipped += 1
                    continue

                subject, body = _build_email(member.full_name, plan.name, membership.end_date, t)
                try:
                    self.email_svc.send(
                        smtp_host=cfg.smtp_host,
                        smtp_port=cfg.smtp_port or 587,
                        smtp_user=cfg.smtp_user,
                        smtp_password_encrypted=cfg.smtp_password_encrypted,
                        from_name=cfg.smtp_from_name or "Gym",
                        from_email=cfg.smtp_from_email or cfg.smtp_user,
                        to_email=member.email,
                        subject=subject,
                        body_html=body,
                    )
                    self.repo.log_attempt(
                        membership_id=membership.id, member_id=member.id,
                        threshold_days=t, channel="email", status="sent",
                        error_message=None, recipient=member.email, sent_at=now,
                    )
                    sent_pairs.add((membership.id, t))  # prevent duplicate within same run
                    notified_membership_ids.append(membership.id)
                    sent += 1
                except Exception as exc:
                    self.repo.log_attempt(
                        membership_id=membership.id, member_id=member.id,
                        threshold_days=t, channel="email", status="failed",
                        error_message=str(exc)[:500], recipient=member.email, sent_at=now,
                    )
                    failed += 1

        if notified_membership_ids:
            self.repo.bulk_update_last_notified(list(set(notified_membership_ids)), now)

        msg = f"{sent} enviados, {skipped} omitidos (ya notificados), {failed} fallidos."
        return NotificationRunResult(sent=sent, skipped=skipped, failed=failed, message=msg)

    # ── History & status ──────────────────────────────────────────────────────

    def get_history(self, page: int = 1, page_size: int = 20) -> NotificationHistoryResponse:
        data = self.repo.get_history(page, page_size)
        return NotificationHistoryResponse(
            items=[NotificationLogRead(**item) for item in data["items"]],
            total=data["total"],
            page=data["page"],
            pages=data["pages"],
        )

    def get_status(self) -> NotificationStatusPanel:
        return NotificationStatusPanel(**self.repo.get_operational_status())
