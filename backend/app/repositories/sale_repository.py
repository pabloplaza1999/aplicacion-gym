"""Sale and sale item repository — Fase B: customer_id, SaleStatus."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from app.models.sale import Sale, SaleItem
from app.models.customer import Customer, CreditPayment
from app.models.inventory import InventoryMovement
from app.models.product import Product


class SaleRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_sale(
        self,
        customer_id: Optional[int],
        payment_type: str,
        subtotal: float,
        discount: float,
        total: float,
        notes: Optional[str],
        status: str,
    ) -> Sale:
        sale = Sale(
            customer_id=customer_id,
            payment_type=payment_type,
            subtotal=subtotal,
            discount=discount,
            total=total,
            notes=notes,
            status=status,
        )
        self.db.add(sale)
        self.db.flush()
        return sale

    def create_sale_item(
        self,
        sale_id: int,
        product_id: int,
        quantity: int,
        unit_price: float,
    ) -> SaleItem:
        item = SaleItem(
            sale_id=sale_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=round(unit_price * quantity, 2),
        )
        self.db.add(item)
        return item

    def get_sale_by_id(self, sale_id: int) -> Optional[Sale]:
        return self.db.query(Sale).filter(Sale.id == sale_id).first()

    def get_sales(
        self,
        customer_id: Optional[int] = None,
        status: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Sale]:
        q = self.db.query(Sale)
        if customer_id:
            q = q.filter(Sale.customer_id == customer_id)
        if status:
            q = q.filter(Sale.status == status)
        if from_date:
            q = q.filter(Sale.sale_date >= from_date)
        if to_date:
            q = q.filter(Sale.sale_date <= to_date)
        return q.order_by(Sale.sale_date.desc()).offset(skip).limit(limit).all()

    def count_sales(
        self,
        customer_id: Optional[int] = None,
        status: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> int:
        q = self.db.query(Sale)
        if customer_id:
            q = q.filter(Sale.customer_id == customer_id)
        if status:
            q = q.filter(Sale.status == status)
        if from_date:
            q = q.filter(Sale.sale_date >= from_date)
        if to_date:
            q = q.filter(Sale.sale_date <= to_date)
        return q.count()

    def sum_sales(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        status: str = "PAID",
    ) -> float:
        q = self.db.query(func.sum(Sale.total)).filter(Sale.status == status)
        if from_date:
            q = q.filter(Sale.sale_date >= from_date)
        if to_date:
            q = q.filter(Sale.sale_date <= to_date)
        return q.scalar() or 0.0

    def get_items_by_sale(self, sale_id: int) -> List[SaleItem]:
        return self.db.query(SaleItem).filter(SaleItem.sale_id == sale_id).all()

    def set_sale_status(self, sale_id: int, status: str) -> Optional[Sale]:
        sale = self.get_sale_by_id(sale_id)
        if not sale:
            return None
        sale.status = status
        return sale

    def product_has_completed_sales(self, product_id: int) -> bool:
        return (
            self.db.query(SaleItem)
            .join(Sale, SaleItem.sale_id == Sale.id)
            .filter(SaleItem.product_id == product_id, Sale.status == "PAID")
            .count()
        ) > 0

    def get_sale_ids_by_product(self, product_id: int) -> List[int]:
        rows = (
            self.db.query(SaleItem.sale_id)
            .filter(SaleItem.product_id == product_id)
            .distinct().all()
        )
        return [r[0] for r in rows]

    def delete_items_by_product(self, product_id: int) -> None:
        self.db.query(SaleItem).filter(
            SaleItem.product_id == product_id
        ).delete(synchronize_session=False)

    def delete_empty_sales(self, sale_ids: List[int]) -> None:
        if not sale_ids:
            return
        sales_with_items = {
            r[0] for r in
            self.db.query(SaleItem.sale_id)
            .filter(SaleItem.sale_id.in_(sale_ids))
            .distinct().all()
        }
        to_delete = [sid for sid in sale_ids if sid not in sales_with_items]
        if not to_delete:
            return
        # TD-21: clean credit_payments before deleting sales to prevent orphaned records
        self.db.query(CreditPayment).filter(
            CreditPayment.sale_id.in_(to_delete)
        ).delete(synchronize_session=False)
        self.db.query(Sale).filter(Sale.id.in_(to_delete)).delete(synchronize_session=False)

    def delete_sale_cascade(self, sale: Sale) -> None:
        """Delete a sale and all its dependent records (credit_payments, movements, items)."""
        # TD-21: credit_payments must be deleted before the sale to prevent orphaned records
        self.db.query(CreditPayment).filter(CreditPayment.sale_id == sale.id).delete()
        self.db.query(InventoryMovement).filter(InventoryMovement.sale_id == sale.id).delete()
        self.db.execute(text("DELETE FROM sale_items WHERE sale_id = :sid"), {"sid": sale.id})
        self.db.delete(sale)

    def purge_orphaned_cancelled(self) -> int:
        """Delete CANCELLED sales with no valid customer (null or deleted customer_id).

        Covers two cases:
          1. customer_id IS NULL (anonymous sales that were cancelled)
          2. customer_id references a customer row that no longer exists (deleted customer)
        Returns the count of deleted sales.
        """
        valid_ids = {r[0] for r in self.db.query(Customer.id).all()}
        sales = (
            self.db.query(Sale)
            .filter(Sale.status == 'CANCELLED')
            .filter(
                Sale.customer_id.is_(None) |
                (~Sale.customer_id.in_(valid_ids) if valid_ids else Sale.customer_id.isnot(None))
            )
            .all()
        )
        for sale in sales:
            self.delete_sale_cascade(sale)
        return len(sales)

    def get_cartera(
        self,
        status_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Sale]:
        statuses = [status_filter] if status_filter in ('PENDING', 'PARTIAL') else ['PENDING', 'PARTIAL']
        return (
            self.db.query(Sale)
            .filter(Sale.status.in_(statuses))
            .order_by(Sale.sale_date.asc())
            .offset(skip).limit(limit).all()
        )

    def get_cartera_kpis(self) -> dict:
        statuses = ['PENDING', 'PARTIAL']
        sale_count = self.db.query(Sale).filter(Sale.status.in_(statuses)).count()
        customer_count = (
            self.db.query(func.count(func.distinct(Sale.customer_id)))
            .filter(Sale.status.in_(statuses), Sale.customer_id.isnot(None))
            .scalar() or 0
        )
        total_sale_amt = (
            self.db.query(func.coalesce(func.sum(Sale.total), 0.0))
            .filter(Sale.status.in_(statuses))
            .scalar() or 0.0
        )
        total_paid = (
            self.db.query(func.coalesce(func.sum(CreditPayment.amount), 0.0))
            .join(Sale, CreditPayment.sale_id == Sale.id)
            .filter(Sale.status.in_(statuses))
            .scalar() or 0.0
        )
        return {
            "total_balance": round(float(total_sale_amt) - float(total_paid), 2),
            "sale_count": sale_count,
            "customer_count": customer_count,
        }

    def get_customer_name(self, customer_id: int) -> Optional[str]:
        c = self.db.query(Customer).filter(Customer.id == customer_id).first()
        return c.name if c else None

    def get_product_name(self, product_id: int) -> Optional[str]:
        p = self.db.query(Product).filter(Product.id == product_id).first()
        return p.name if p else None

    # ── Aggregate queries for store reports (Fase C) ──────────────────────────

    def get_sales_kpis(self, date_from: datetime, date_to: datetime) -> dict:
        """KPI aggregates for the sales report (excludes CANCELLED)."""
        active = ['PAID', 'PARTIAL', 'PENDING']
        f = [Sale.status.in_(active), Sale.sale_date >= date_from, Sale.sale_date <= date_to]

        total_sales = self.db.query(Sale).filter(*f).count()
        total_revenue = float(
            self.db.query(func.coalesce(func.sum(Sale.total), 0.0)).filter(*f).scalar() or 0.0
        )
        cash_count = self.db.query(Sale).filter(*f, Sale.payment_type == 'cash').count()
        cash_amount = float(
            self.db.query(func.coalesce(func.sum(Sale.total), 0.0))
            .filter(*f, Sale.payment_type == 'cash').scalar() or 0.0
        )
        credit_count = self.db.query(Sale).filter(*f, Sale.payment_type == 'credit').count()
        credit_amount = float(
            self.db.query(func.coalesce(func.sum(Sale.total), 0.0))
            .filter(*f, Sale.payment_type == 'credit').scalar() or 0.0
        )
        return {
            'total_sales': total_sales,
            'total_revenue': round(total_revenue, 2),
            'cash_sales_count': cash_count,
            'cash_sales_amount': round(cash_amount, 2),
            'credit_sales_count': credit_count,
            'credit_sales_amount': round(credit_amount, 2),
            'average_ticket': round(total_revenue / total_sales, 2) if total_sales else 0.0,
        }

    def get_credit_collections(self, date_from: datetime, date_to: datetime) -> float:
        """Sum of credit payments received in the period (by paid_at, excludes CANCELLED sales)."""
        result = (
            self.db.query(func.coalesce(func.sum(CreditPayment.amount), 0.0))
            .join(Sale, CreditPayment.sale_id == Sale.id)
            .filter(
                Sale.status != 'CANCELLED',
                CreditPayment.paid_at >= date_from,
                CreditPayment.paid_at <= date_to,
            )
            .scalar()
        )
        return round(float(result or 0.0), 2)

    def get_top_debtors(self, limit: int = 5) -> list:
        """Top customers by outstanding balance, ordered DESC.

        Returns list of (customer_id, customer_name, outstanding_balance, oldest_sale_date).
        Reuses PENDING/PARTIAL logic consistent with get_cartera_kpis().
        """
        statuses = ['PENDING', 'PARTIAL']
        outstanding_expr = (
            func.sum(Sale.total) - func.coalesce(func.sum(CreditPayment.amount), 0.0)
        )
        rows = (
            self.db.query(
                Customer.id,
                Customer.name,
                outstanding_expr.label('outstanding'),
                func.min(Sale.sale_date).label('oldest_sale_date'),
            )
            .join(Sale, Sale.customer_id == Customer.id)
            .outerjoin(CreditPayment, CreditPayment.sale_id == Sale.id)
            .filter(Sale.status.in_(statuses), Sale.customer_id.isnot(None))
            .group_by(Customer.id, Customer.name)
            .having(outstanding_expr > 0)
            .order_by(outstanding_expr.desc())
            .limit(limit)
            .all()
        )
        return rows

    def get_cartera_kpis_for_report(self) -> dict:
        """Extends get_cartera_kpis() with per-status counts and oldest debt date."""
        base = self.get_cartera_kpis()
        statuses = ['PENDING', 'PARTIAL']
        pending_count = self.db.query(Sale).filter(Sale.status == 'PENDING').count()
        partial_count = self.db.query(Sale).filter(Sale.status == 'PARTIAL').count()
        oldest = (
            self.db.query(func.min(Sale.sale_date))
            .filter(Sale.status.in_(statuses))
            .scalar()
        )
        return {
            **base,
            'outstanding_balance': base['total_balance'],
            'customers_with_debt': base['customer_count'],
            'pending_sales_count': pending_count,
            'partial_sales_count': partial_count,
            'oldest_debt_date': oldest,
        }
