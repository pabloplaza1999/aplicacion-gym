"""Membership service for business logic."""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.membership_repository import MembershipRepository
from app.schemas.membership import (
    MembershipCreate,
    MembershipRead,
    MembershipRenew,
    MembershipWithPlanRead,
    VoucherWarning,
)

# Maximum freeze/unfreeze cycles allowed per membership (TD-13).
MAX_FREEZE_CYCLES = 3


class MembershipNotFoundError(Exception):
    """Raised when a membership_id does not exist."""


class FreezeLimitReachedError(ValueError):
    """Raised when a membership has reached MAX_FREEZE_CYCLES."""


class ActiveVoucherExistsError(Exception):
    """Raised when a member already has an active, valid voucher.

    Business rule: a member may hold only ONE active voucher at a time.
    A new voucher cannot be sold/activated while another active voucher is
    still valid (not expired and with entries remaining).
    """


class MembershipService:
    """Service for membership business logic operations."""

    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.repository = MembershipRepository(db)
        self.attendance_repo = AttendanceRepository(db)
        self.db = db

    def _calculate_status(
        self, end_date: datetime, is_active: bool = True, frozen_at: Optional[datetime] = None
    ) -> str:
        """
        Calculate membership status.

        Rules:
        - frozen:   is_active=False AND frozen_at is set (paused, days preserved)
        - inactive: is_active=False AND frozen_at is None (manually deactivated)
        - expired:  end_date < today
        - expiring: today <= end_date <= today + 5 days
        - active:   end_date > today + 5 days
        """
        if not is_active:
            return "frozen" if frozen_at is not None else "inactive"

        today = datetime.utcnow()
        days_remaining = (end_date - today).days

        if days_remaining < 0:
            return "expired"
        elif days_remaining <= 5:
            return "expiring"
        else:
            return "active"

    def _calculate_end_date(self, start_date: datetime, plan_id: int) -> datetime:
        """
        Calculate end date based on plan duration.

        Rules:
        - Plan Día (plan_type='daily'): vence el mismo día
        - Plans mensuales: 30 días desde start_date
        """
        plan = self.repository.get_plan_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        if plan.plan_type == "daily":
            return start_date.replace(hour=23, minute=59, second=59)
        else:
            return start_date + timedelta(days=plan.duration_days)

    def _enrich_membership(self, membership, plan=None):
        """
        Enrich membership with calculated status and plan details.

        Passes frozen_at to _calculate_status so frozen state is reflected.
        For voucher memberships, overrides status to 'exhausted' when all
        entries have been consumed but the membership is still within date (TD-01).
        """
        if plan is None:
            plan = self.repository.get_plan_by_id(membership.plan_id)

        data = MembershipRead.from_orm(membership)
        data.status = self._calculate_status(
            membership.end_date, membership.is_active, membership.frozen_at
        )

        # TD-01: voucher agotada — status override using the same attendance source
        # of truth as _has_active_valid_voucher and get_active_voucher_warning.
        if (
            plan
            and plan.plan_type == "voucher"
            and membership.entries_total is not None
            and data.status not in ("expired", "inactive", "frozen")
        ):
            used = self.attendance_repo.count_by_membership(membership.id)
            if used >= membership.entries_total:
                data.status = "exhausted"

        today = datetime.utcnow()
        days_remaining = max(0, (membership.end_date - today).days)

        return {
            **data.model_dump(),
            "days_remaining": days_remaining,
            "plan_name": plan.name if plan else None,
            "plan_price": plan.price if plan else None,
            "plan_duration_days": plan.duration_days if plan else None,
        }

    def _has_active_valid_voucher(self, member_id: int) -> bool:
        """
        Whether the member holds an active voucher that is still valid.

        A voucher blocks a new one only when ALL hold:
        - is_active == True and plan_type == "voucher" (repo filter)
        - not expired (end_date >= now)
        - entries remaining > 0, using COUNT(attendances) as source of truth

        An exhausted or expired voucher does NOT block. Date-based (monthly)
        memberships are never considered here.
        """
        membership = self.repository.get_active_voucher_membership(member_id)
        if not membership or membership.entries_total is None:
            return False

        now = datetime.utcnow()
        if membership.end_date < now:
            return False

        used = self.attendance_repo.count_by_membership(membership.id)
        remaining = membership.entries_total - used
        return remaining > 0

    def get_active_voucher_warning(self, member_id: int) -> VoucherWarning:
        """
        Retorna info de la valera activa vigente del cliente, si existe.

        Usado antes de crear/renovar a plan mensual para mostrar advertencia
        y pedir confirmación al operador.
        """
        membership = self.repository.get_active_voucher_membership(member_id)
        if not membership or membership.entries_total is None:
            return VoucherWarning(has_active_voucher=False)

        now = datetime.utcnow()
        if membership.end_date < now:
            return VoucherWarning(has_active_voucher=False)

        used = self.attendance_repo.count_by_membership(membership.id)
        remaining = membership.entries_total - used
        if remaining <= 0:
            return VoucherWarning(has_active_voucher=False)

        plan = self.repository.get_plan_by_id(membership.plan_id)
        return VoucherWarning(
            has_active_voucher=True,
            membership_id=membership.id,
            plan_name=plan.name if plan else None,
            entries_remaining=remaining,
            end_date=membership.end_date.date().isoformat(),
        )

    def create_membership(self, data: MembershipCreate) -> MembershipRead:
        """
        Create a new membership.

        Automatically calculates end_date based on plan duration.

        Business rule: a member can hold at most one active non-voucher membership
        at a time. If one exists when creating a new non-voucher, it is deactivated
        atomically (same pattern as renew_membership).

        Raises:
            ActiveVoucherExistsError: when creating a voucher membership while
                the member already has an active, valid voucher.
        """
        start_date = data.start_date or datetime.utcnow()
        end_date = self._calculate_end_date(start_date, data.plan_id)

        plan = self.repository.get_plan_by_id(data.plan_id)
        entries_total = plan.entry_count if plan and plan.plan_type == "voucher" else None

        if plan and plan.plan_type == "voucher" and self._has_active_valid_voucher(data.member_id):
            raise ActiveVoucherExistsError(
                "El cliente ya tiene una valera activa vigente. "
                "No se puede vender otra hasta que se agote o venza."
            )

        if plan and plan.plan_type != "voucher" and data.force:
            active_voucher = self.repository.get_active_voucher_membership(data.member_id)
            if active_voucher:
                self.repository.set_active(active_voucher.id, False)

        # Enforce one-active-non-voucher rule: deactivate previous non-voucher if present.
        if plan and plan.plan_type != "voucher":
            existing = self.repository.get_active_non_voucher_membership(data.member_id)
            if existing:
                self.repository.deactivate_no_commit(existing.id)

        membership = self.repository.create(
            member_id=data.member_id,
            plan_id=data.plan_id,
            start_date=start_date,
            end_date=end_date,
            entries_total=entries_total,
        )

        result = MembershipRead.from_orm(membership)
        result.status = self._calculate_status(membership.end_date)
        return result

    def get_membership(self, membership_id: int) -> Optional[MembershipWithPlanRead]:
        """Get a membership by ID with plan details."""
        membership = self.repository.get_by_id(membership_id)
        if not membership:
            return None

        plan = self.repository.get_plan_by_id(membership.plan_id)
        enriched = self._enrich_membership(membership, plan)
        return MembershipWithPlanRead(**enriched)

    def get_member_memberships(
        self, member_id: int, skip: int = 0, limit: int = 100
    ) -> dict:
        """Get all memberships for a member."""
        memberships = self.repository.get_by_member_id(member_id, skip=skip, limit=limit)
        total = self.repository.get_by_member_id_count(member_id)

        items = []
        for m in memberships:
            result = MembershipRead.from_orm(m)
            result.status = self._calculate_status(m.end_date, m.is_active)
            items.append(result)

        return {"total": total, "items": items}

    def get_current_membership(self, member_id: int) -> Optional[MembershipWithPlanRead]:
        """Get the current (most recent) membership for a member."""
        membership = self.repository.get_active_membership(member_id)
        if not membership:
            return None

        plan = self.repository.get_plan_by_id(membership.plan_id)
        enriched = self._enrich_membership(membership, plan)
        return MembershipWithPlanRead(**enriched)

    def renew_membership(self, membership_id: int, data: MembershipRenew) -> MembershipRead:
        """
        Renew a membership with a new plan.

        Creates a new membership starting from today.
        """
        old_membership = self.repository.get_by_id(membership_id)
        if not old_membership:
            raise ValueError(f"Membership {membership_id} not found")

        new_plan = self.repository.get_plan_by_id(data.plan_id)

        if (
            new_plan
            and new_plan.plan_type == "voucher"
            and self._has_active_valid_voucher(old_membership.member_id)
        ):
            raise ActiveVoucherExistsError(
                "El cliente ya tiene una valera activa vigente. "
                "No se puede vender otra hasta que se agote o venza."
            )

        if new_plan and new_plan.plan_type != "voucher" and data.force:
            active_voucher = self.repository.get_active_voucher_membership(old_membership.member_id)
            if active_voucher:
                self.repository.set_active(active_voucher.id, False)

        start_date = datetime.utcnow()
        end_date = self._calculate_end_date(start_date, data.plan_id)

        entries_total = (
            new_plan.entry_count if new_plan and new_plan.plan_type == "voucher" else None
        )

        self.repository.deactivate_no_commit(old_membership.id)

        new_membership = self.repository.create(
            member_id=old_membership.member_id,
            plan_id=data.plan_id,
            start_date=start_date,
            end_date=end_date,
            entries_total=entries_total,
        )

        result = MembershipRead.from_orm(new_membership)
        result.status = self._calculate_status(new_membership.end_date)
        return result

    def set_membership_active(
        self, membership_id: int, is_active: bool
    ) -> Optional[MembershipWithPlanRead]:
        """
        Manually activate or deactivate a membership.

        Blocked while the membership is frozen; use unfreeze_membership instead.
        Blocked when activating a non-voucher membership while another non-voucher
        is already active for the same member (one-active-non-voucher rule).
        """
        membership = self.repository.get_by_id(membership_id)
        if not membership:
            return None
        if membership.frozen_at is not None:
            raise ValueError(
                "La membresía está congelada. Usa 'Reactivar' para restaurarla con los días pendientes."
            )

        if is_active:
            plan = self.repository.get_plan_by_id(membership.plan_id)
            if plan and plan.plan_type != "voucher":
                conflict = self.repository.get_active_non_voucher_membership(
                    membership.member_id, exclude_id=membership_id
                )
                if conflict:
                    raise ValueError(
                        "El cliente ya tiene una membresía activa. "
                        "Desactívala primero antes de reactivar esta."
                    )

        updated = self.repository.set_active(membership_id, is_active)
        plan = self.repository.get_plan_by_id(updated.plan_id)
        enriched = self._enrich_membership(updated, plan)
        return MembershipWithPlanRead(**enriched)

    def freeze_membership(self, membership_id: int) -> MembershipWithPlanRead:
        """
        Freeze a membership: save days_remaining and set is_active=False.

        Preconditions: is_active=True, not already frozen, end_date > now,
        freeze_count < MAX_FREEZE_CYCLES.
        Persistence delegated to repository.freeze() which commits in one transaction.
        """
        membership = self.repository.get_by_id(membership_id)
        if not membership:
            raise MembershipNotFoundError(f"Membresía {membership_id} no encontrada.")
        if not membership.is_active:
            raise ValueError("La membresía ya está inactiva o congelada.")
        if membership.frozen_at is not None:
            raise ValueError("La membresía ya está congelada.")
        if (membership.freeze_count or 0) >= MAX_FREEZE_CYCLES:
            raise FreezeLimitReachedError(
                f"Esta membresía ya alcanzó el límite de {MAX_FREEZE_CYCLES} congelaciones."
            )
        now = datetime.utcnow()
        if membership.end_date <= now:
            raise ValueError("No se puede congelar una membresía vencida.")

        days_remaining = (membership.end_date - now).days
        updated = self.repository.freeze(
            membership_id, frozen_at=now, frozen_days_remaining=days_remaining
        )
        plan = self.repository.get_plan_by_id(updated.plan_id)
        enriched = self._enrich_membership(updated, plan)
        return MembershipWithPlanRead(**enriched)

    def unfreeze_membership(self, membership_id: int) -> MembershipWithPlanRead:
        """
        Unfreeze a membership: new end_date = now + frozen_days_remaining.

        Accumulates freeze_days with elapsed days. Clears freeze fields.
        Persistence delegated to repository.unfreeze() which commits in one transaction.
        """
        membership = self.repository.get_by_id(membership_id)
        if not membership:
            raise MembershipNotFoundError(f"Membresía {membership_id} no encontrada.")
        if membership.frozen_at is None:
            raise ValueError("La membresía no está congelada.")

        now = datetime.utcnow()
        elapsed = now - membership.frozen_at
        # Extend the original end_date by exact elapsed time — avoids floor-division day loss.
        new_end_date = membership.end_date + elapsed
        freeze_days_delta = elapsed.days

        updated = self.repository.unfreeze(
            membership_id, new_end_date=new_end_date, freeze_days_delta=freeze_days_delta
        )
        plan = self.repository.get_plan_by_id(updated.plan_id)
        enriched = self._enrich_membership(updated, plan)
        return MembershipWithPlanRead(**enriched)

    def get_expiring_memberships(self, days: int = 5) -> list[MembershipWithPlanRead]:
        """Get memberships expiring within the specified number of days."""
        memberships = self.repository.get_expiring_soon(days=days)

        results = []
        for m in memberships:
            plan = self.repository.get_plan_by_id(m.plan_id)
            enriched = self._enrich_membership(m, plan)
            results.append(MembershipWithPlanRead(**enriched))

        return results
