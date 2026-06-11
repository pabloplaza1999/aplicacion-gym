"""Credit payment service — Tienda Fase B."""

from typing import List
from sqlalchemy.orm import Session

from app.repositories.sale_repository import SaleRepository
from app.repositories.credit_payment_repository import CreditPaymentRepository
from app.schemas.credit_payment import CreditPaymentCreate, CreditPaymentRead


class CannotPayCancelledSaleError(ValueError):
    pass


class ExceedsBalanceError(ValueError):
    pass


class CreditPaymentService:

    def __init__(self, db: Session):
        self.sale_repo = SaleRepository(db)
        self.cp_repo = CreditPaymentRepository(db)
        self.db = db

    def register_payment(self, sale_id: int, data: CreditPaymentCreate) -> CreditPaymentRead:
        sale = self.sale_repo.get_sale_by_id(sale_id)
        if not sale:
            raise ValueError("Venta no encontrada.")
        if sale.status == "CANCELLED":
            raise CannotPayCancelledSaleError("No se puede abonar a una venta anulada.")
        if sale.status == "PAID":
            raise ValueError("Esta venta ya está completamente pagada.")
        if sale.status not in ("PENDING", "PARTIAL"):
            raise ValueError(f"Estado de venta inválido: {sale.status}.")

        amount_paid = self.cp_repo.sum_by_sale(sale_id)
        balance = round(sale.total - amount_paid, 2)

        if data.amount > balance + 0.01:
            raise ExceedsBalanceError(
                f"El monto abonado ({data.amount:.0f}) supera el saldo pendiente ({balance:.0f})."
            )
        amount = min(data.amount, balance)

        payment = self.cp_repo.create(sale_id=sale_id, amount=amount, method=data.method, notes=data.notes)
        self.db.flush()

        new_paid = round(amount_paid + amount, 2)
        new_status = "PAID" if new_paid >= sale.total - 0.01 else "PARTIAL"
        self.sale_repo.set_sale_status(sale_id, new_status)

        self.db.commit()
        self.db.refresh(payment)
        return CreditPaymentRead(
            id=payment.id, sale_id=payment.sale_id, amount=payment.amount,
            method=payment.method, notes=payment.notes,
            paid_at=payment.paid_at, created_at=payment.created_at,
        )

    def get_payments_by_sale(self, sale_id: int) -> List[CreditPaymentRead]:
        sale = self.sale_repo.get_sale_by_id(sale_id)
        if not sale:
            raise ValueError("Venta no encontrada.")
        payments = self.cp_repo.get_by_sale(sale_id)
        return [
            CreditPaymentRead(
                id=p.id, sale_id=p.sale_id, amount=p.amount, method=p.method,
                notes=p.notes, paid_at=p.paid_at, created_at=p.created_at,
            )
            for p in payments
        ]
