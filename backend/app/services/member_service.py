"""Member service for business logic."""

from typing import Optional, List

from sqlalchemy.orm import Session

from app.repositories.member_repository import MemberRepository
from app.schemas.member import MemberCreate, MemberUpdate, MemberRead


class DuplicateDocumentError(Exception):
    """Raised when a member with the same document number already exists."""


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

        Raises:
            DuplicateDocumentError: If a member with the same document already exists.
        """
        if data.document:
            if self.repository.get_by_document(data.document):
                raise DuplicateDocumentError()
        member = self.repository.create(
            full_name=data.full_name,
            phone=data.phone,
            document=data.document,
            email=data.email,
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
        """Permanently delete a member and all related data.

        Raises:
            ValueError: If the member has active store sales (PAID/PENDING/PARTIAL).
        """
        if self.repository.has_active_sales(member_id):
            raise ValueError("No se puede eliminar un cliente con ventas activas (PAID, PENDING o PARTIAL).")
        return self.repository.hard_delete(member_id)

    def get_members_for_store(
        self,
        q: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[MemberRead]:
        """List/search members for the store customer selector."""
        if q:
            members = self.repository.search_for_store(q, skip=skip, limit=limit)
        else:
            members = self.repository.get_all(skip=skip, limit=limit)
        return [MemberRead.from_orm(m) for m in members]

    def delete_customer_from_store(self, member_id: int) -> None:
        """Delete a member via the store tab.

        Raises:
            ValueError: If the member has active sales or gym memberships.
        """
        if not self.repository.get_by_id(member_id):
            raise ValueError("Cliente no encontrado.")
        if self.repository.has_active_sales(member_id):
            raise ValueError("No se puede eliminar un cliente con ventas activas (PAID, PENDING o PARTIAL).")
        if self.repository.has_memberships(member_id):
            raise ValueError("Este cliente tiene membresías del gimnasio. Elimínelo desde el módulo Clientes.")
        self.repository.hard_delete(member_id)
