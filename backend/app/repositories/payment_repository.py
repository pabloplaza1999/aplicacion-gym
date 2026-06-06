"""Payment repository."""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.payment import Payment
from app.models.member import Member


class PaymentRepository:
    """Repository for payment operations."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def create(self, member_id: int, amount: float, payment_method: str, membership_id: int = None, payment_date: datetime = None) -> Payment:
        """Create a new payment.
        
        Args:
            member_id: Member ID
            amount: Payment amount
            payment_method: Payment method (cash, transfer, qr, nequi)
            membership_id: Optional membership ID
            payment_date: Optional payment date (defaults to now)
            
        Returns:
            Created Payment instance
        """
        if payment_date is None:
            payment_date = datetime.utcnow()
            
        payment = Payment(
            member_id=member_id,
            membership_id=membership_id,
            amount=amount,
            payment_method=payment_method,
            payment_date=payment_date
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_by_id(self, payment_id: int) -> Payment:
        """Get payment by ID."""
        return self.db.query(Payment).filter(Payment.id == payment_id).first()

    def get_by_member_id(self, member_id: int, skip: int = 0, limit: int = 10) -> list[Payment]:
        """Get all payments for a member."""
        return self.db.query(Payment)\
            .filter(Payment.member_id == member_id)\
            .order_by(Payment.payment_date.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_by_member_id_count(self, member_id: int) -> int:
        """Get total count of payments for a member."""
        return self.db.query(Payment)\
            .filter(Payment.member_id == member_id)\
            .count()

    def get_all(self, skip: int = 0, limit: int = 10) -> list[Payment]:
        """Get all payments."""
        return self.db.query(Payment)\
            .order_by(Payment.payment_date.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_all_with_member(self, skip: int = 0, limit: int = 10) -> list[tuple]:
        """Get all payments joined with member name."""
        return self.db.query(Payment, Member.full_name)\
            .join(Member, Payment.member_id == Member.id)\
            .order_by(Payment.payment_date.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_all_count(self) -> int:
        """Get total count of payments."""
        return self.db.query(Payment).count()

    def get_by_method(self, payment_method: str, skip: int = 0, limit: int = 10) -> list[Payment]:
        """Get payments by method."""
        return self.db.query(Payment)\
            .filter(Payment.payment_method == payment_method)\
            .order_by(Payment.payment_date.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_by_method_count(self, payment_method: str) -> int:
        """Get count of payments by method."""
        return self.db.query(Payment)\
            .filter(Payment.payment_method == payment_method)\
            .count()

    def get_by_method_total(self, payment_method: str) -> float:
        """Get total amount for a payment method."""
        result = self.db.query(Payment)\
            .filter(Payment.payment_method == payment_method)\
            .with_entities(func.sum(Payment.amount))\
            .scalar()
        return result or 0.0

    def get_by_date_range(self, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 10) -> list[Payment]:
        """Get payments within a date range."""
        return self.db.query(Payment)\
            .filter(Payment.payment_date >= start_date)\
            .filter(Payment.payment_date <= end_date)\
            .order_by(Payment.payment_date.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_by_date_range_count(self, start_date: datetime, end_date: datetime) -> int:
        """Get count of payments within a date range."""
        return self.db.query(Payment)\
            .filter(Payment.payment_date >= start_date)\
            .filter(Payment.payment_date <= end_date)\
            .count()

    def get_by_date_range_total(self, start_date: datetime, end_date: datetime) -> float:
        """Get total amount for a date range."""
        result = self.db.query(Payment)\
            .filter(Payment.payment_date >= start_date)\
            .filter(Payment.payment_date <= end_date)\
            .with_entities(func.sum(Payment.amount))\
            .scalar()
        return result or 0.0

    def get_by_month(self, year: int, month: int, skip: int = 0, limit: int = 10) -> list[Payment]:
        """Get payments for a specific month."""
        # Start of month
        start_date = datetime(year, month, 1)
        # End of month
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        return self.get_by_date_range(start_date, end_date, skip, limit)

    def get_by_month_count(self, year: int, month: int) -> int:
        """Get count of payments for a specific month."""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        return self.get_by_date_range_count(start_date, end_date)

    def get_by_month_total(self, year: int, month: int) -> float:
        """Get total amount for a specific month."""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        return self.get_by_date_range_total(start_date, end_date)

    def get_total_amount(self) -> float:
        """Get total amount of all payments."""
        result = self.db.query(Payment)\
            .with_entities(func.sum(Payment.amount))\
            .scalar()
        return result or 0.0

    def get_total_by_member(self, member_id: int) -> float:
        """Get total amount paid by a member."""
        result = self.db.query(Payment)\
            .filter(Payment.member_id == member_id)\
            .with_entities(func.sum(Payment.amount))\
            .scalar()
        return result or 0.0

    def get_statistics_by_method(self) -> dict:
        """Get payment statistics by method."""
        stats = {}
        for method in ["cash", "transfer", "qr", "nequi"]:
            count = self.get_by_method_count(method)
            total = self.get_by_method_total(method)
            stats[method] = {
                "count": count,
                "total": total
            }
        return stats
    def delete(self, payment_id: int) -> bool:
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            return False
        self.db.delete(payment)
        self.db.commit()
        return True
