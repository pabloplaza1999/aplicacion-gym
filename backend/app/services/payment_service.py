"""Payment service."""

from datetime import datetime, timedelta
from app.repositories.payment_repository import PaymentRepository
from app.schemas.payment import PaymentCreate, PaymentRead, PaymentListResponse, PaymentsByMemberResponse, PaymentStatistics, PaymentsByMethodResponse
from sqlalchemy.orm import Session


class PaymentService:
    """Service for payment operations."""

    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.repository = PaymentRepository(db)
        self.db = db

    def create_payment(self, data: PaymentCreate) -> PaymentRead:
        """Create a new payment.
        
        Args:
            data: PaymentCreate schema with payment details
            
        Returns:
            PaymentRead with created payment data
        """
        # Validate payment method
        valid_methods = ["cash", "transfer", "qr", "nequi"]
        if data.payment_method not in valid_methods:
            raise ValueError(f"Invalid payment method. Must be one of: {', '.join(valid_methods)}")
        
        # Validate amount
        if data.amount <= 0:
            raise ValueError("Amount must be greater than 0")
        
        # Create payment
        payment = self.repository.create(
            member_id=data.member_id,
            membership_id=data.membership_id,
            amount=data.amount,
            payment_method=data.payment_method
        )
        
        return PaymentRead.from_orm(payment)

    def get_payment(self, payment_id: int) -> PaymentRead | None:
        """Get payment by ID."""
        payment = self.repository.get_by_id(payment_id)
        if not payment:
            return None
        return PaymentRead.from_orm(payment)

    def get_member_payments(self, member_id: int, skip: int = 0, limit: int = 10) -> PaymentsByMemberResponse:
        """Get all payments for a member with statistics."""
        total = self.repository.get_by_member_id_count(member_id)
        payments = self.repository.get_by_member_id(member_id, skip, limit)
        
        # Calculate total amount
        amount_total = self.repository.get_total_by_member(member_id)
        
        return PaymentsByMemberResponse(
            total=total,
            amount_total=amount_total,
            items=[PaymentRead.from_orm(p) for p in payments]
        )

    def get_all_payments(self, skip: int = 0, limit: int = 10) -> PaymentListResponse:
        """Get all payments with pagination, including member name."""
        total = self.repository.get_all_count()
        rows = self.repository.get_all_with_member(skip, limit)
        total_amount = self.repository.get_total_amount()

        items = [
            PaymentRead(
                id=payment.id,
                member_id=payment.member_id,
                membership_id=payment.membership_id,
                amount=payment.amount,
                payment_method=payment.payment_method,
                payment_date=payment.payment_date,
                member_name=full_name,
            )
            for payment, full_name in rows
        ]

        return PaymentListResponse(
            total=total,
            total_amount=total_amount,
            items=items,
        )

    def get_payments_by_method(self, payment_method: str, skip: int = 0, limit: int = 10) -> PaymentListResponse:
        """Get payments by method."""
        # Validate method
        valid_methods = ["cash", "transfer", "qr", "nequi"]
        if payment_method not in valid_methods:
            raise ValueError(f"Invalid payment method. Must be one of: {', '.join(valid_methods)}")
        
        total = self.repository.get_by_method_count(payment_method)
        payments = self.repository.get_by_method(payment_method, skip, limit)
        total_amount = self.repository.get_by_method_total(payment_method)
        
        return PaymentListResponse(
            total=total,
            total_amount=total_amount,
            items=[PaymentRead.from_orm(p) for p in payments]
        )

    def get_payments_by_date_range(self, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 10) -> PaymentListResponse:
        """Get payments within a date range."""
        total = self.repository.get_by_date_range_count(start_date, end_date)
        payments = self.repository.get_by_date_range(start_date, end_date, skip, limit)
        total_amount = self.repository.get_by_date_range_total(start_date, end_date)
        
        return PaymentListResponse(
            total=total,
            total_amount=total_amount,
            items=[PaymentRead.from_orm(p) for p in payments]
        )

    def get_monthly_payments(self, year: int, month: int, skip: int = 0, limit: int = 10) -> PaymentListResponse:
        """Get payments for a specific month."""
        # Validate month
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")
        
        total = self.repository.get_by_month_count(year, month)
        payments = self.repository.get_by_month(year, month, skip, limit)
        total_amount = self.repository.get_by_month_total(year, month)
        
        return PaymentListResponse(
            total=total,
            total_amount=total_amount,
            items=[PaymentRead.from_orm(p) for p in payments]
        )

    def get_payment_statistics(self) -> PaymentStatistics:
        """Get payment statistics by method."""
        stats = self.repository.get_statistics_by_method()
        total_payments = self.repository.get_all_count()
        total_amount = self.repository.get_total_amount()
        
        # Build by_method list
        by_method_list = []
        for method, data in stats.items():
            percentage = (data["total"] / total_amount * 100) if total_amount > 0 else 0
            by_method_list.append(PaymentsByMethodResponse(
                method=method,
                count=data["count"],
                total_amount=data["total"],
                percentage=round(percentage, 2)
            ))
        
        # Sort by total_amount descending
        by_method_list.sort(key=lambda x: x.total_amount, reverse=True)
        
        return PaymentStatistics(
            total_payments=total_payments,
            total_amount=total_amount,
            by_method=by_method_list
        )

    def get_current_month_statistics(self) -> PaymentStatistics:
        """Get payment statistics for current month."""
        now = datetime.utcnow()
        year = now.year
        month = now.month
        
        # Get start and end of month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        # Get payments for the month
        monthly_payments = self.repository.get_by_date_range(start_date, end_date, skip=0, limit=10000)
        total_payments = self.repository.get_by_date_range_count(start_date, end_date)
        total_amount = self.repository.get_by_date_range_total(start_date, end_date)
        
        # Calculate by method for the month
        by_method_list = []
        for method in ["cash", "transfer", "qr", "nequi"]:
            method_payments = [p for p in monthly_payments if p.payment_method == method]
            method_total = sum(p.amount for p in method_payments)
            percentage = (method_total / total_amount * 100) if total_amount > 0 else 0
            
            if method_payments:  # Only include methods with payments
                by_method_list.append(PaymentsByMethodResponse(
                    method=method,
                    count=len(method_payments),
                    total_amount=method_total,
                    percentage=round(percentage, 2)
                ))
        
        # Sort by total_amount descending
        by_method_list.sort(key=lambda x: x.total_amount, reverse=True)
        
        return PaymentStatistics(
            total_payments=total_payments,
            total_amount=total_amount,
            by_method=by_method_list,
            payment_date_range=f"{start_date.date()} to {end_date.date()}"
        )
    def delete_payment(self, payment_id: int) -> bool:
        return self.repository.delete(payment_id)
