"""Customer service — Tienda Fase B."""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate


class CustomerService:

    def __init__(self, db: Session):
        self.repo = CustomerRepository(db)
        self.db = db

    def _enrich(self, c) -> CustomerRead:
        member_name = self.repo.get_member_name(c.member_id) if c.member_id else None
        debt_total = self.repo.get_debt_total(c.id)
        return CustomerRead(
            id=c.id, name=c.name, document=c.document, phone=c.phone,
            email=c.email, notes=c.notes, member_id=c.member_id,
            member_name=member_name, debt_total=debt_total, created_at=c.created_at,
        )

    def create_customer(self, data: CustomerCreate) -> CustomerRead:
        if data.document:
            existing = self.repo.get_by_document(data.document)
            if existing:
                raise ValueError(f"Ya existe un cliente con el documento '{data.document}'.")
        c = self.repo.create(
            name=data.name, document=data.document, phone=data.phone,
            email=data.email, notes=data.notes,
        )
        self.db.commit()
        self.db.refresh(c)
        return self._enrich(c)

    def get_or_create_from_member(self, member_id: int) -> CustomerRead:
        """Get or create a Customer linked to a gym member."""
        from app.models.member import Member
        existing = self.repo.get_by_member_id(member_id)
        if existing:
            return self._enrich(existing)
        member = self.db.query(Member).filter(Member.id == member_id).first()
        if not member:
            raise ValueError("Miembro no encontrado.")
        c = self.repo.create(
            name=member.full_name,
            document=member.document,
            phone=member.phone,
            member_id=member_id,
        )
        self.db.commit()
        self.db.refresh(c)
        return self._enrich(c)

    def search_customers(self, q: str, skip: int = 0, limit: int = 20) -> List[CustomerRead]:
        results = self.repo.search(q, skip=skip, limit=limit)
        return [self._enrich(c) for c in results]

    def get_customers(self, skip: int = 0, limit: int = 50) -> List[CustomerRead]:
        results = self.repo.get_all(skip=skip, limit=limit)
        return [self._enrich(c) for c in results]

    def get_customer(self, customer_id: int) -> CustomerRead:
        c = self.repo.get_by_id(customer_id)
        if not c:
            raise ValueError("Cliente no encontrado.")
        return self._enrich(c)

    def delete_customer(self, customer_id: int) -> None:
        c = self.repo.get_by_id(customer_id)
        if not c:
            raise ValueError("Cliente no encontrado.")
        if self.repo.has_active_sales(customer_id):
            raise ValueError("No se puede eliminar un cliente con ventas activas (PAID, PENDING o PARTIAL).")
        self.repo.delete_cancelled_sales(customer_id)
        self.repo.delete(customer_id)
        self.db.commit()

    def update_customer(self, customer_id: int, data: CustomerUpdate) -> CustomerRead:
        c = self.repo.get_by_id(customer_id)
        if not c:
            raise ValueError("Cliente no encontrado.")
        fields = data.model_dump(exclude_none=True)
        if 'document' in fields and fields['document']:
            existing = self.repo.get_by_document(fields['document'])
            if existing and existing.id != customer_id:
                raise ValueError(f"Ya existe un cliente con el documento '{fields['document']}'.")
        updated = self.repo.update(customer_id, **fields)
        self.db.commit()
        self.db.refresh(updated)
        return self._enrich(updated)
