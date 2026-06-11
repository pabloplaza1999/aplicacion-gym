"""Customer repository — Tienda Fase B."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, text

from app.models.customer import Customer, CreditPayment
from app.models.sale import Sale
from app.models.inventory import InventoryMovement
from app.models.member import Member


class CustomerRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        name: str,
        document: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        notes: Optional[str] = None,
        member_id: Optional[int] = None,
    ) -> Customer:
        c = Customer(name=name, document=document, phone=phone,
                     email=email, notes=notes, member_id=member_id)
        self.db.add(c)
        return c

    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def get_by_document(self, document: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.document == document).first()

    def get_by_member_id(self, member_id: int) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.member_id == member_id).first()

    def get_all(self, skip: int = 0, limit: int = 50) -> List[Customer]:
        return self.db.query(Customer).order_by(Customer.name).offset(skip).limit(limit).all()

    def count_all(self) -> int:
        return self.db.query(Customer).count()

    def search(self, q: str, skip: int = 0, limit: int = 50) -> List[Customer]:
        pattern = f"%{q}%"
        return (
            self.db.query(Customer)
            .filter(or_(
                Customer.name.ilike(pattern),
                Customer.document.ilike(pattern),
                Customer.phone.ilike(pattern),
            ))
            .order_by(Customer.name)
            .offset(skip).limit(limit).all()
        )

    def update(self, customer_id: int, **kwargs) -> Optional[Customer]:
        c = self.get_by_id(customer_id)
        if not c:
            return None
        for k, v in kwargs.items():
            if hasattr(c, k):
                setattr(c, k, v)
        return c

    def has_active_sales(self, customer_id: int) -> bool:
        return (
            self.db.query(Sale)
            .filter(Sale.customer_id == customer_id, Sale.status != 'CANCELLED')
            .first() is not None
        )

    def delete_cancelled_sales(self, customer_id: int) -> None:
        """Delete all CANCELLED sales for this customer, including their items and movements."""
        cancelled = (
            self.db.query(Sale)
            .filter(Sale.customer_id == customer_id, Sale.status == 'CANCELLED')
            .all()
        )
        for sale in cancelled:
            self.db.query(InventoryMovement).filter(InventoryMovement.sale_id == sale.id).delete()
            self.db.execute(text("DELETE FROM sale_items WHERE sale_id = :sid"), {"sid": sale.id})
            self.db.delete(sale)

    def delete(self, customer_id: int) -> bool:
        c = self.get_by_id(customer_id)
        if not c:
            return False
        self.db.delete(c)
        return True

    def get_member_name(self, member_id: int) -> Optional[str]:
        m = self.db.query(Member).filter(Member.id == member_id).first()
        return m.full_name if m else None

    def get_debt_total(self, customer_id: int) -> float:
        """Sum of (sale.total - paid) for PENDING/PARTIAL sales of this customer."""
        statuses = ['PENDING', 'PARTIAL']
        total_sales = (
            self.db.query(func.coalesce(func.sum(Sale.total), 0.0))
            .filter(Sale.customer_id == customer_id, Sale.status.in_(statuses))
            .scalar() or 0.0
        )
        total_paid = (
            self.db.query(func.coalesce(func.sum(CreditPayment.amount), 0.0))
            .join(Sale, CreditPayment.sale_id == Sale.id)
            .filter(Sale.customer_id == customer_id, Sale.status.in_(statuses))
            .scalar() or 0.0
        )
        return round(float(total_sales) - float(total_paid), 2)
