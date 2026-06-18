"""Dashboard repository — aggregated queries for KPI endpoint."""

from collections import defaultdict
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import BOGOTA_OFFSET
from app.models.member import Member
from app.models.membership import Membership
from app.models.attendance import Attendance
from app.models.payment import Payment
from app.models.plan import Plan

# Priority for Best State Wins. Higher = better state for the client.
_STATE_PRIORITY = {"active": 5, "expiring": 4, "exhausted": 3, "frozen": 2, "expired": 1}


class DashboardRepository:
    """Efficient aggregated queries for dashboard KPIs."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------ #
    # Members                                                              #
    # ------------------------------------------------------------------ #

    def get_active_members_count(self) -> int:
        """Total members with is_active=True."""
        return self.db.query(Member).filter(Member.is_active == True).count()

    # ------------------------------------------------------------------ #
    # Memberships by status                                                #
    # ------------------------------------------------------------------ #

    def get_memberships_by_status(self) -> dict:
        """Count each member's membership status using Best State Wins.

        A client with multiple simultaneous active memberships (Option D) is
        classified by the best state among all their memberships:
            active > expiring > exhausted > frozen > expired

        A client with a monthly (active) + Plan Día (expired) counts as 'active'.
        Plain inactive memberships (is_active=False, frozen_at=None) are skipped.
        Attendance count resolved via correlated subquery (TD-01).
        """
        attendance_count_sq = (
            self.db.query(func.count(Attendance.id))
            .filter(Attendance.membership_id == Membership.id)
            .correlate(Membership)
            .scalar_subquery()
        )

        rows = (
            self.db.query(
                Membership.member_id,
                Membership.end_date,
                Membership.is_active,
                Membership.frozen_at,
                Membership.entries_total,
                Plan.plan_type,
                attendance_count_sq.label("used"),
            )
            .join(Plan, Membership.plan_id == Plan.id)
            .join(Member, Membership.member_id == Member.id)
            .filter(Member.is_active == True)
            .all()
        )

        member_best: dict = {}
        now = datetime.utcnow() + BOGOTA_OFFSET

        for member_id, end_date, is_active, frozen_at, entries_total, plan_type, used in rows:
            if not is_active:
                if frozen_at is not None:
                    state = "frozen"
                else:
                    continue  # plain inactive (historical) — skip
            else:
                days_remaining = (end_date - now).days
                if days_remaining < 0:
                    state = "expired"
                elif plan_type == "voucher" and entries_total is not None and (used or 0) >= entries_total:
                    state = "exhausted"
                elif days_remaining <= 5:
                    state = "expiring"
                else:
                    state = "active"

            current_best = member_best.get(member_id)
            if current_best is None or _STATE_PRIORITY[state] > _STATE_PRIORITY[current_best]:
                member_best[member_id] = state

        result = {"active": 0, "expiring": 0, "expired": 0, "frozen": 0, "exhausted": 0}
        for state in member_best.values():
            result[state] += 1
        return result

    # ------------------------------------------------------------------ #
    # Members by plan                                                      #
    # ------------------------------------------------------------------ #

    def get_members_by_plan(self) -> list:
        """Count memberships classified by plan and status — no global dedup.

        Each active membership is counted independently in its plan (Option D).
        A client with a monthly + Plan Día contributes to both plan rows.

        Categories:
          active     — is_active=True, end_date >= now, not exhausted
          exhausted  — voucher, is_active=True, end_date >= now, used >= entries_total
          expired    — is_active=True, end_date < now
          frozen     — is_active=False, frozen_at IS NOT NULL

        Plain inactive (is_active=False, frozen_at=None) memberships are skipped.
        Plans with zero memberships in all categories are excluded.
        Ordered by total DESC.
        """
        attendance_count_sq = (
            self.db.query(func.count(Attendance.id))
            .filter(Attendance.membership_id == Membership.id)
            .correlate(Membership)
            .scalar_subquery()
        )

        rows = (
            self.db.query(
                Membership.end_date,
                Membership.is_active,
                Membership.frozen_at,
                Membership.entries_total,
                Plan.id.label("plan_id"),
                Plan.name.label("plan_name"),
                Plan.plan_type,
                attendance_count_sq.label("used"),
            )
            .join(Plan, Membership.plan_id == Plan.id)
            .join(Member, Membership.member_id == Member.id)
            .filter(Member.is_active == True)
            .all()
        )

        now = datetime.utcnow() + BOGOTA_OFFSET
        plan_counts: dict = {}

        for row in rows:
            plan_id = row.plan_id
            if plan_id not in plan_counts:
                plan_counts[plan_id] = {
                    "plan_id": plan_id,
                    "plan_name": row.plan_name,
                    "plan_type": row.plan_type,
                    "active_count": 0,
                    "exhausted_count": 0,
                    "expired_count": 0,
                    "frozen_count": 0,
                }

            if not row.is_active:
                if row.frozen_at is not None:
                    plan_counts[plan_id]["frozen_count"] += 1
                continue  # plain inactive — skip

            days_remaining = (row.end_date - now).days
            if days_remaining < 0:
                plan_counts[plan_id]["expired_count"] += 1
            elif row.plan_type == "voucher" and row.entries_total is not None and (row.used or 0) >= row.entries_total:
                plan_counts[plan_id]["exhausted_count"] += 1
            else:
                plan_counts[plan_id]["active_count"] += 1

        result = []
        for p in plan_counts.values():
            total = p["active_count"] + p["exhausted_count"] + p["expired_count"] + p["frozen_count"]
            if total == 0:
                continue
            result.append({**p, "total": total})

        result.sort(key=lambda x: x["total"], reverse=True)
        return result

    # ------------------------------------------------------------------ #
    # Revenue                                                              #
    # ------------------------------------------------------------------ #

    def get_monthly_revenue(self, year: int, month: int) -> float:
        """Total payment amount for a given month."""
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end = datetime(year, month + 1, 1) - timedelta(seconds=1)

        result = (
            self.db.query(func.sum(Payment.amount))
            .filter(Payment.payment_date >= start, Payment.payment_date <= end)
            .scalar()
        )
        return result or 0.0

    def get_revenue_by_plan(self, year: int, month: int) -> list:
        """Revenue grouped by plan for a given month via JOIN."""
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end = datetime(year, month + 1, 1) - timedelta(seconds=1)

        rows = (
            self.db.query(
                Plan.id,
                Plan.name,
                func.count(Payment.id),
                func.sum(Payment.amount),
            )
            .join(Membership, Payment.membership_id == Membership.id)
            .join(Plan, Membership.plan_id == Plan.id)
            .filter(
                Payment.payment_date >= start,
                Payment.payment_date <= end,
                Payment.membership_id.isnot(None),
            )
            .group_by(Plan.id, Plan.name)
            .order_by(func.sum(Payment.amount).desc())
            .all()
        )
        return rows

    # ------------------------------------------------------------------ #
    # Recent renewals                                                      #
    # ------------------------------------------------------------------ #

    def get_recent_renewals(self, limit: int = 5) -> list:
        """Most recent memberships with member name, plan name and last payment."""
        rows = (
            self.db.query(
                Membership.id,
                Membership.member_id,
                Member.full_name,
                Plan.name,
                Membership.start_date,
                Membership.end_date,
                func.max(Payment.amount),
            )
            .join(Member, Membership.member_id == Member.id)
            .join(Plan, Membership.plan_id == Plan.id)
            .outerjoin(Payment, Payment.membership_id == Membership.id)
            .group_by(
                Membership.id,
                Membership.member_id,
                Member.full_name,
                Plan.name,
                Membership.start_date,
                Membership.end_date,
            )
            .order_by(Membership.start_date.desc())
            .limit(limit)
            .all()
        )
        return rows

    # ------------------------------------------------------------------ #
    # Membership alerts                                                    #
    # ------------------------------------------------------------------ #

    def get_membership_alerts(self, per_group_limit: int = 50) -> dict:
        """Return clients requiring action, classified into 4 urgency groups.

        Unit of analysis: CLIENT (not individual membership).
        Uses Best State Wins — same priority as get_memberships_by_status():
            active > expiring > exhausted > frozen > expired

        Suppression rule: a client with ANY membership with >5 days remaining
        (state='active') is suppressed from ALL alert buckets. Only clients
        with best_state='expiring' or 'expired' appear.

        Exhausted and frozen clients are suppressed (covered by StatCards).

        Representative membership per client:
          expired bucket  → most recently expired membership (highest end_date)
          upcoming buckets → soonest expiring membership (lowest end_date, diff>=0)

        All plan types included (monthly, daily, voucher).
        Exhausted vouchers within date are treated as 'exhausted', not 'expiring'.

        Groups (Bogota local dates):
          expired     — best_state=expired (ordered DESC by end_date)
          today       — best_state=expiring, soonest end_date == today
          three_days  — best_state=expiring, soonest end_date in 1–3 days
          seven_days  — best_state=expiring, soonest end_date in 4–5 days
        Each group capped at per_group_limit rows.
        """
        today = (datetime.utcnow() + BOGOTA_OFFSET).date()

        attendance_count_sq = (
            self.db.query(func.count(Attendance.id))
            .filter(Attendance.membership_id == Membership.id)
            .correlate(Membership)
            .scalar_subquery()
        )

        rows = (
            self.db.query(
                Membership.id.label("membership_id"),
                Membership.member_id,
                Member.full_name,
                Member.phone,
                Member.document,
                Plan.name,
                Plan.plan_type,
                Membership.end_date,
                Membership.entries_total,
                attendance_count_sq.label("used"),
            )
            .join(Member, Membership.member_id == Member.id)
            .join(Plan, Membership.plan_id == Plan.id)
            .filter(
                Member.is_active == True,
                Membership.is_active == True,
            )
            .all()
        )

        # Classify each membership and group by client
        member_memberships: dict = defaultdict(list)

        for row in rows:
            end = (row.end_date + BOGOTA_OFFSET).date() if hasattr(row.end_date, "date") else row.end_date
            diff = (end - today).days

            if diff < 0:
                state = "expired"
            elif row.plan_type == "voucher" and row.entries_total is not None and (row.used or 0) >= row.entries_total:
                state = "exhausted"
            elif diff <= 5:
                state = "expiring"
            else:
                state = "active"

            member_memberships[row.member_id].append({
                "membership_id": row.membership_id,
                "member_id": row.member_id,
                "member_name": row.full_name,
                "phone": row.phone,
                "document": row.document,
                "plan_name": row.name,
                "end": end,
                "diff": diff,
                "state": state,
            })

        expired, today_items, three_days, seven_days = [], [], [], []

        for member_id, memberships in member_memberships.items():
            # Suppress: client has at least one fully active membership (>5 days)
            if any(m["state"] == "active" for m in memberships):
                continue

            best_state = max(memberships, key=lambda m: _STATE_PRIORITY[m["state"]])["state"]

            # Only expiring and expired clients appear in alerts
            if best_state not in ("expiring", "expired"):
                continue

            def _item(m: dict, days_overdue: int = 0) -> dict:
                return {
                    "membership_id": m["membership_id"],
                    "member_id": m["member_id"],
                    "member_name": m["member_name"],
                    "phone": m["phone"],
                    "document": m["document"],
                    "plan_name": m["plan_name"],
                    "end_date": m["end"],
                    "days_overdue": days_overdue,
                }

            if best_state == "expired":
                # Show most recently expired membership (highest end_date)
                rep = max(
                    [m for m in memberships if m["state"] == "expired"],
                    key=lambda m: m["end"],
                )
                expired.append(_item(rep, abs(rep["diff"])))

            else:  # expiring
                # Show soonest expiring membership (lowest end_date, diff >= 0)
                rep = min(
                    [m for m in memberships if m["state"] == "expiring"],
                    key=lambda m: m["end"],
                )
                diff = rep["diff"]
                if diff == 0:
                    today_items.append(_item(rep))
                elif diff <= 3:
                    three_days.append(_item(rep))
                else:
                    seven_days.append(_item(rep))

        def by_end(x):
            return x["end_date"]

        expired.sort(key=by_end, reverse=True)
        today_items.sort(key=by_end)
        three_days.sort(key=by_end)
        seven_days.sort(key=by_end)

        return {
            "expired": expired[:per_group_limit],
            "today": today_items[:per_group_limit],
            "three_days": three_days[:per_group_limit],
            "seven_days": seven_days[:per_group_limit],
        }
