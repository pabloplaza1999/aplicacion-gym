"""Sale business logic — Cliente Único: member_id es la columna canónica."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.repositories.member_repository import MemberRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.sale_repository import SaleRepository
from app.repositories.credit_payment_repository import CreditPaymentRepository
from app.schemas.sale import (
    SaleCreate, SaleRead, SaleItemRead, SaleListResponse,
    CarteraKPI, CarteraResponse,
    SalesKPI, TopProductItem, LowStockItem, CarteraReport, InventoryReport, StoreReportResponse,
)


class InsufficientStockError(ValueError):
    """Raised when a sale item exceeds available stock."""


class CannotCancelPartialSaleError(ValueError):
    """Raised when trying to cancel a sale that already has partial payments."""


class SaleService:

    def __init__(self, db: Session):
        self.member_repo = MemberRepository(db)
        self.product_repo = ProductRepository(db)
        self.inventory_repo = InventoryRepository(db)
        self.sale_repo = SaleRepository(db)
        self.cp_repo = CreditPaymentRepository(db)
        self.db = db

    def _enrich_sale(self, sale) -> dict:
        items = self.sale_repo.get_items_by_sale(sale.id)
        # Cliente Único: member_id is canonical; exposed as customer_id for frontend compat
        effective_member_id = sale.member_id
        customer_name = self.sale_repo.get_member_name(effective_member_id) if effective_member_id else None
        amount_paid = self.cp_repo.sum_by_sale(sale.id)
        balance = round(sale.total - amount_paid, 2) if sale.status in ('PENDING', 'PARTIAL') else 0.0
        enriched_items = [
            SaleItemRead(
                id=item.id,
                product_id=item.product_id,
                product_name=self.sale_repo.get_product_name(item.product_id),
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
            )
            for item in items
        ]
        return {
            "id": sale.id,
            "customer_id": effective_member_id,
            "customer_name": customer_name,
            "sale_date": sale.sale_date,
            "subtotal": sale.subtotal,
            "discount": sale.discount,
            "total": sale.total,
            "payment_type": sale.payment_type,
            "notes": sale.notes,
            "status": sale.status,
            "amount_paid": amount_paid,
            "balance": balance,
            "items": enriched_items,
            "created_at": sale.created_at,
        }

    def create_sale(self, data: SaleCreate) -> SaleRead:
        if data.payment_type == "credit" and not data.customer_id:
            raise ValueError("Las ventas a crédito requieren un cliente.")

        if data.customer_id:
            if not self.member_repo.get_by_id(data.customer_id):
                raise ValueError("Cliente no encontrado.")

        products = []
        for item in data.items:
            product = self.product_repo.get_product_by_id(item.product_id)
            if not product:
                raise ValueError(f"Producto ID {item.product_id} no encontrado.")
            if not product.is_active:
                raise ValueError(f"El producto '{product.name}' está inactivo.")
            if product.stock < item.quantity:
                raise InsufficientStockError(
                    f"Stock insuficiente para '{product.name}'. "
                    f"Disponible: {product.stock}, solicitado: {item.quantity}."
                )
            products.append(product)

        subtotal = sum(
            round(products[i].price * data.items[i].quantity, 2)
            for i in range(len(data.items))
        )
        discount = round(data.discount, 2)
        total = round(max(0.0, subtotal - discount), 2)
        status = "PENDING" if data.payment_type == "credit" else "PAID"

        # SaleCreate.customer_id contains a member_id (semantic reuse — zero frontend change)
        sale = self.sale_repo.create_sale(
            member_id=data.customer_id,
            payment_type=data.payment_type,
            subtotal=subtotal,
            discount=discount,
            total=total,
            notes=data.notes,
            status=status,
        )

        for i, item in enumerate(data.items):
            product = products[i]
            self.sale_repo.create_sale_item(
                sale_id=sale.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=product.price,
            )
            stock_before = product.stock
            stock_after = stock_before - item.quantity
            product.stock = stock_after
            self.inventory_repo.create_movement(
                product_id=item.product_id,
                movement_type="sale",
                quantity=-item.quantity,
                stock_before=stock_before,
                stock_after=stock_after,
                sale_id=sale.id,
            )

        self.db.commit()
        self.db.refresh(sale)
        return SaleRead(**self._enrich_sale(sale))

    def get_sale(self, sale_id: int) -> SaleRead:
        sale = self.sale_repo.get_sale_by_id(sale_id)
        if not sale:
            raise ValueError("Venta no encontrada.")
        return SaleRead(**self._enrich_sale(sale))

    def get_sales(
        self,
        customer_id: Optional[int] = None,
        status: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> SaleListResponse:
        sales = self.sale_repo.get_sales(
            customer_id=customer_id, status=status,
            from_date=from_date, to_date=to_date,
            skip=skip, limit=limit,
        )
        total = self.sale_repo.count_sales(
            customer_id=customer_id, status=status,
            from_date=from_date, to_date=to_date,
        )
        total_amount = self.sale_repo.sum_sales(from_date=from_date, to_date=to_date, status="PAID")
        return SaleListResponse(
            total=total,
            total_amount=total_amount,
            items=[SaleRead(**self._enrich_sale(s)) for s in sales],
        )

    def purge_orphaned_cancelled(self) -> int:
        count = self.sale_repo.purge_orphaned_cancelled()
        self.db.commit()
        return count

    def get_cartera(
        self,
        status_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> CarteraResponse:
        sales = self.sale_repo.get_cartera(status_filter=status_filter, skip=skip, limit=limit)
        kpi_data = self.sale_repo.get_cartera_kpis()
        return CarteraResponse(
            items=[SaleRead(**self._enrich_sale(s)) for s in sales],
            kpi=CarteraKPI(**kpi_data),
        )

    def cancel_sale(self, sale_id: int, note: str = None) -> SaleRead:
        sale = self.sale_repo.get_sale_by_id(sale_id)
        if not sale:
            raise ValueError("Venta no encontrada.")
        if sale.status == "CANCELLED":
            raise ValueError("La venta ya está anulada.")
        if sale.status == "PARTIAL":
            raise CannotCancelPartialSaleError(
                "Esta venta tiene abonos registrados y no puede anularse automáticamente."
            )

        items = self.sale_repo.get_items_by_sale(sale_id)
        for item in items:
            product = self.product_repo.get_product_by_id(item.product_id)
            if product:
                stock_before = product.stock
                stock_after = stock_before + item.quantity
                product.stock = stock_after
                self.inventory_repo.create_movement(
                    product_id=item.product_id,
                    movement_type="adjustment",
                    quantity=item.quantity,
                    stock_before=stock_before,
                    stock_after=stock_after,
                    note=f"Anulación venta #{sale_id}" + (f" — {note}" if note else ""),
                    sale_id=sale_id,
                )

        self.sale_repo.set_sale_status(sale_id, "CANCELLED")
        self.db.commit()
        self.db.refresh(sale)
        return SaleRead(**self._enrich_sale(sale))

    def get_store_report(self, date_from: datetime, date_to: datetime) -> StoreReportResponse:
        sales_kpis = self.sale_repo.get_sales_kpis(date_from, date_to)
        sales_kpis['credit_collections_amount'] = self.sale_repo.get_credit_collections(date_from, date_to)

        cartera = self.sale_repo.get_cartera_kpis_for_report()
        top = self.product_repo.get_top_products(date_from, date_to, limit=5)

        cats = {c.id: c.name for c in self.product_repo.get_categories()}
        low_stock_prods = self.product_repo.get_products(low_stock=True, active_only=True, limit=10)

        return StoreReportResponse(
            date_from=date_from,
            date_to=date_to,
            sales=SalesKPI(**sales_kpis),
            top_products=[TopProductItem(**p) for p in top],
            cartera=CarteraReport(
                outstanding_balance=cartera['outstanding_balance'],
                customers_with_debt=cartera['customers_with_debt'],
                pending_sales_count=cartera['pending_sales_count'],
                partial_sales_count=cartera['partial_sales_count'],
                oldest_debt_date=cartera['oldest_debt_date'],
            ),
            inventory=InventoryReport(
                low_stock_count=len(low_stock_prods),
                low_stock_products=[
                    LowStockItem(
                        product_id=p.id,
                        product_name=p.name,
                        stock=p.stock,
                        min_stock=p.min_stock,
                        category_name=cats.get(p.category_id),
                    )
                    for p in low_stock_prods
                ],
            ),
        )
