"""Credit payment repository — Tienda Fase B."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.customer import CreditPayment


class CreditPaymentRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        sale_id: int,
        amount: float,
        method: str,
        notes: Optional[str] = None,
    ) -> CreditPayment:
        p = CreditPayment(sale_id=sale_id, amount=round(amount, 2), method=method, notes=notes)
        self.db.add(p)
        return p

    def get_by_sale(self, sale_id: int) -> List[CreditPayment]:
        return (
            self.db.query(CreditPayment)
            .filter(CreditPayment.sale_id == sale_id)
            .order_by(CreditPayment.paid_at)
            .all()
        )

    def sum_by_sale(self, sale_id: int) -> float:
        result = (
            self.db.query(func.coalesce(func.sum(CreditPayment.amount), 0.0))
            .filter(CreditPayment.sale_id == sale_id)
            .scalar()
        )
        return float(result) if result else 0.0
