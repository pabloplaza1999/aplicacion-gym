"""Member repository for data access."""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.member import Member


class MemberRepository:
    """Repository for member data access operations."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def create(self, full_name: str, phone: str, document: Optional[str] = None, email: Optional[str] = None, notes: Optional[str] = None) -> Member:
        """
        Create a new member.

        Args:
            full_name: Full name of the member
            phone: Phone number
            document: Optional document/ID
            email: Optional email address
            notes: Optional notes

        Returns:
            Created member instance
        """
        member = Member(
            full_name=full_name,
            phone=phone,
            document=document,
            email=email,
            notes=notes,
        )
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def get_by_document(self, document: str) -> Optional[Member]:
        """Get member by document number."""
        return self.db.query(Member).filter(Member.document == document).first()

    def get_by_id(self, member_id: int) -> Optional[Member]:
        """Get member by ID."""
        return self.db.query(Member).filter(Member.id == member_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Member]:
        """
        Get all members with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of members
        """
        return self.db.query(Member).offset(skip).limit(limit).all()

    def get_all_count(self) -> int:
        """Get total count of members."""
        return self.db.query(Member).count()

    def search(self, search_term: str, skip: int = 0, limit: int = 100) -> list[Member]:
        """
        Search members by name or phone.

        Args:
            search_term: Search term (name or phone)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching members
        """
        search_pattern = f"%{search_term}%"
        return (
            self.db.query(Member)
            .filter(
                (Member.full_name.ilike(search_pattern))
                | (Member.phone.ilike(search_pattern))
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_count(self, search_term: str) -> int:
        """Get count of search results."""
        search_pattern = f"%{search_term}%"
        return (
            self.db.query(Member)
            .filter(
                (Member.full_name.ilike(search_pattern))
                | (Member.phone.ilike(search_pattern))
            )
            .count()
        )

    def update(self, member_id: int, **kwargs) -> Optional[Member]:
        """
        Update a member.

        Args:
            member_id: Member ID
            **kwargs: Fields to update

        Returns:
            Updated member or None if not found
        """
        member = self.get_by_id(member_id)
        if not member:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(member, key):
                setattr(member, key, value)

        self.db.commit()
        self.db.refresh(member)
        return member

    def deactivate(self, member_id: int) -> Optional[Member]:
        """
        Deactivate a member.

        Args:
            member_id: Member ID

        Returns:
            Updated member or None if not found
        """
        return self.update(member_id, is_active=False)

    def get_by_phone(self, phone: str) -> Optional[Member]:
        """Get member by phone number."""
        return self.db.query(Member).filter(Member.phone == phone).first()

    def get_by_document(self, document: str) -> Optional[Member]:
        """Get member by document."""
        return (
            self.db.query(Member).filter(Member.document == document).first()
        )

    def hard_delete(self, member_id: int) -> bool:
        """Permanently delete a member and all related data."""
        member = self.get_by_id(member_id)
        if not member:
            return False

        # Delete related body measurements
        from app.models.body_measurement import BodyMeasurement
        self.db.query(BodyMeasurement).filter(BodyMeasurement.member_id == member_id).delete()

        # Delete related payments
        from app.models.payment import Payment
        self.db.query(Payment).filter(Payment.member_id == member_id).delete()

        # Delete related memberships
        from app.models.membership import Membership
        self.db.query(Membership).filter(Membership.member_id == member_id).delete()

        # Delete the member
        self.db.delete(member)
        self.db.commit()
        return True

    def has_active_sales(self, member_id: int) -> bool:
        from app.models.sale import Sale
        return (
            self.db.query(Sale)
            .filter(Sale.member_id == member_id, Sale.status.in_(['PAID', 'PENDING', 'PARTIAL']))
            .first()
        ) is not None

    def get_debt_total(self, member_id: int) -> float:
        from sqlalchemy import func
        from app.models.sale import Sale
        from app.models.customer import CreditPayment
        statuses = ['PENDING', 'PARTIAL']
        total_sales = (
            self.db.query(func.coalesce(func.sum(Sale.total), 0.0))
            .filter(Sale.member_id == member_id, Sale.status.in_(statuses))
            .scalar() or 0.0
        )
        total_paid = (
            self.db.query(func.coalesce(func.sum(CreditPayment.amount), 0.0))
            .join(Sale, CreditPayment.sale_id == Sale.id)
            .filter(Sale.member_id == member_id, Sale.status.in_(statuses))
            .scalar() or 0.0
        )
        return round(float(total_sales) - float(total_paid), 2)

    def search_for_store(self, q: str, skip: int = 0, limit: int = 50) -> list[Member]:
        """Search by name, phone, or document — used by store customer alias."""
        pattern = f"%{q}%"
        return (
            self.db.query(Member)
            .filter(
                Member.full_name.ilike(pattern)
                | Member.phone.ilike(pattern)
                | Member.document.ilike(pattern)
            )
            .offset(skip).limit(limit).all()
        )

    def has_memberships(self, member_id: int) -> bool:
        from app.models.membership import Membership
        return (
            self.db.query(Membership).filter(Membership.member_id == member_id).first()
        ) is not None
