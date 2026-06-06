"""Attendance service — voucher check-in business logic.

All logic here applies ONLY to voucher memberships (plan_type == "voucher").
Traditional memberships are never touched by this module.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.membership_repository import MembershipRepository
from app.schemas.attendance import CheckInResult, VoucherStatus


class CheckInError(Exception):
    """Business error carrying an HTTP status code and a user message."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class AttendanceService:
    """Service for attendance / voucher consumption."""

    def __init__(self, db: Session):
        self.db = db
        self.attendance_repo = AttendanceRepository(db)
        self.member_repo = MemberRepository(db)
        self.membership_repo = MembershipRepository(db)

    def _resolve_voucher(self, document: str):
        """Resolve (member, membership, plan) for an active voucher by document.

        Raises CheckInError when the member or an active voucher does not exist.
        """
        document = (document or "").strip()
        if not document:
            raise CheckInError(400, "Debe ingresar la cédula del cliente")

        member = self.member_repo.get_by_document(document)
        if not member:
            raise CheckInError(404, "No existe un cliente con esa cédula")

        membership = self.membership_repo.get_active_voucher_membership(member.id)
        if not membership:
            raise CheckInError(404, "El cliente no tiene una valera activa")

        plan = self.membership_repo.get_plan_by_id(membership.plan_id)
        # Guard: apply logic only for voucher memberships with a defined cap.
        if not plan or plan.plan_type != "voucher" or membership.entries_total is None:
            raise CheckInError(400, "La membresía del cliente no es una valera")

        return member, membership, plan

    def check_in(self, document: str) -> CheckInResult:
        """Register an attendance, consuming one voucher entry."""
        member, membership, plan = self._resolve_voucher(document)
        now = datetime.utcnow()
        today = now.date()

        # 1) Vigencia
        if membership.end_date < now:
            raise CheckInError(409, "La valera está vencida")

        # 2) Ingresos disponibles (COUNT = fuente de verdad)
        used = self.attendance_repo.count_by_membership(membership.id)
        remaining = membership.entries_total - used
        if remaining <= 0:
            raise CheckInError(409, "La valera no tiene ingresos disponibles")

        # 3) Una sola asistencia por cliente por día
        if self.attendance_repo.exists_for_member_on_date(member.id, today):
            raise CheckInError(409, "El cliente ya registró asistencia hoy")

        # 4) Registrar (consume 1 ingreso)
        attendance = self.attendance_repo.create(
            member_id=member.id,
            membership_id=membership.id,
            check_in_at=now,
            check_in_date=today,
        )

        used_after = used + 1
        remaining_after = membership.entries_total - used_after
        finished = remaining_after <= 0 or membership.end_date < now

        return CheckInResult(
            member_id=member.id,
            member_name=member.full_name,
            membership_id=membership.id,
            plan_name=plan.name,
            entries_total=membership.entries_total,
            entries_used=used_after,
            entries_remaining=remaining_after,
            end_date=membership.end_date,
            finished=finished,
            check_in_at=attendance.check_in_at,
        )

    def get_voucher_status(self, document: str) -> VoucherStatus:
        """Read-only status of a member's active voucher (no consumption)."""
        member, membership, plan = self._resolve_voucher(document)
        now = datetime.utcnow()

        used = self.attendance_repo.count_by_membership(membership.id)
        remaining = membership.entries_total - used
        finished = remaining <= 0 or membership.end_date < now

        return VoucherStatus(
            member_id=member.id,
            member_name=member.full_name,
            membership_id=membership.id,
            plan_name=plan.name,
            entries_total=membership.entries_total,
            entries_used=used,
            entries_remaining=remaining,
            end_date=membership.end_date,
            attended_today=self.attendance_repo.exists_for_member_on_date(member.id, now.date()),
            finished=finished,
        )
