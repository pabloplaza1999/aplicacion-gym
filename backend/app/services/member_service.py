"""Member service for business logic."""

from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.member_repository import MemberRepository
from app.schemas.member import MemberCreate, MemberUpdate, MemberRead


class MemberService:
    """Service for member business logic operations."""

    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.repository = MemberRepository(db)

    def create_member(self, data: MemberCreate) -> MemberRead:
        """
        Create a new member.

        Args:
            data: Member creation data

        Returns:
            Created member
        """
        member = self.repository.create(
            full_name=data.full_name,
            phone=data.phone,
            document=data.document,
            notes=data.notes,
        )
        return MemberRead.from_orm(member)

    def get_member(self, member_id: int) -> Optional[MemberRead]:
        """Get a member by ID."""
        member = self.repository.get_by_id(member_id)
        if not member:
            return None
        return MemberRead.from_orm(member)

    def list_members(self, skip: int = 0, limit: int = 100) -> dict:
        """
        List all members with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Dictionary with total count and list of members
        """
        members = self.repository.get_all(skip=skip, limit=limit)
        total = self.repository.get_all_count()
        return {
            "total": total,
            "items": [MemberRead.from_orm(m) for m in members],
        }

    def search_members(self, search_term: str, skip: int = 0, limit: int = 100) -> dict:
        """
        Search members by name or phone.

        Args:
            search_term: Search term
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Dictionary with total count and list of matching members
        """
        members = self.repository.search(search_term, skip=skip, limit=limit)
        total = self.repository.search_count(search_term)
        return {
            "total": total,
            "items": [MemberRead.from_orm(m) for m in members],
        }

    def update_member(self, member_id: int, data: MemberUpdate) -> Optional[MemberRead]:
        """
        Update a member.

        Args:
            member_id: Member ID
            data: Update data

        Returns:
            Updated member or None if not found
        """
        update_dict = data.model_dump(exclude_unset=True)
        member = self.repository.update(member_id, **update_dict)
        if not member:
            return None
        return MemberRead.from_orm(member)

    def deactivate_member(self, member_id: int) -> Optional[MemberRead]:
        """
        Deactivate a member.

        Args:
            member_id: Member ID

        Returns:
            Deactivated member or None if not found
        """
        member = self.repository.deactivate(member_id)
        if not member:
            return None
        return MemberRead.from_orm(member)

    def hard_delete_member(self, member_id: int) -> bool:
        """Permanently delete a member and all related data."""
        return self.repository.hard_delete(member_id)
