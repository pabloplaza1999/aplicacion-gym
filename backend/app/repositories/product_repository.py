"""Product and category repository."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.models.product import Product, ProductCategory


class ProductRepository:

    def __init__(self, db: Session):
        self.db = db

    # ── Categories ────────────────────────────────────────────────────────────

    def get_categories(self, active_only: bool = False) -> List[ProductCategory]:
        q = self.db.query(ProductCategory)
        if active_only:
            q = q.filter(ProductCategory.is_active == True)
        return q.order_by(ProductCategory.name).all()

    def get_category_by_id(self, category_id: int) -> Optional[ProductCategory]:
        return self.db.query(ProductCategory).filter(ProductCategory.id == category_id).first()

    def get_category_by_name(self, name: str) -> Optional[ProductCategory]:
        return self.db.query(ProductCategory).filter(ProductCategory.name == name).first()

    def create_category(self, name: str, description: Optional[str]) -> ProductCategory:
        cat = ProductCategory(name=name, description=description)
        self.db.add(cat)
        self.db.commit()
        self.db.refresh(cat)
        return cat

    def update_category(self, category_id: int, **kwargs) -> Optional[ProductCategory]:
        cat = self.get_category_by_id(category_id)
        if not cat:
            return None
        for k, v in kwargs.items():
            if v is not None:
                setattr(cat, k, v)
        self.db.commit()
        self.db.refresh(cat)
        return cat

    def set_category_active(self, category_id: int, is_active: bool) -> Optional[ProductCategory]:
        cat = self.get_category_by_id(category_id)
        if not cat:
            return None
        cat.is_active = is_active
        self.db.commit()
        self.db.refresh(cat)
        return cat

    def delete_category(self, category_id: int) -> bool:
        cat = self.get_category_by_id(category_id)
        if not cat:
            return False
        self.db.delete(cat)
        self.db.commit()
        return True

    def category_has_products(self, category_id: int) -> bool:
        return self.db.query(Product).filter(Product.category_id == category_id).count() > 0

    # ── Products ──────────────────────────────────────────────────────────────

    def get_products(
        self,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        low_stock: bool = False,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Product]:
        q = self.db.query(Product)
        if active_only:
            q = q.filter(Product.is_active == True)
        if category_id:
            q = q.filter(Product.category_id == category_id)
        if search:
            q = q.filter(Product.name.ilike(f"%{search}%"))
        if low_stock:
            q = q.filter(Product.stock <= Product.min_stock, Product.min_stock > 0)
        return q.order_by(Product.name).offset(skip).limit(limit).all()

    def count_products(
        self,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        low_stock: bool = False,
        active_only: bool = False,
    ) -> int:
        q = self.db.query(Product)
        if active_only:
            q = q.filter(Product.is_active == True)
        if category_id:
            q = q.filter(Product.category_id == category_id)
        if search:
            q = q.filter(Product.name.ilike(f"%{search}%"))
        if low_stock:
            q = q.filter(Product.stock <= Product.min_stock, Product.min_stock > 0)
        return q.count()

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_product_by_name(self, name: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.name == name).first()

    def create_product(
        self,
        category_id: int,
        name: str,
        description: Optional[str],
        price: float,
        cost: Optional[float],
        stock: int,
        min_stock: int,
    ) -> Product:
        product = Product(
            category_id=category_id,
            name=name,
            description=description,
            price=price,
            cost=cost,
            stock=stock,
            min_stock=min_stock,
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update_product(self, product_id: int, **kwargs) -> Optional[Product]:
        product = self.get_product_by_id(product_id)
        if not product:
            return None
        for k, v in kwargs.items():
            if v is not None:
                setattr(product, k, v)
        self.db.commit()
        self.db.refresh(product)
        return product

    def set_product_active(self, product_id: int, is_active: bool) -> Optional[Product]:
        product = self.get_product_by_id(product_id)
        if not product:
            return None
        product.is_active = is_active
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete_product(self, product_id: int) -> bool:
        product = self.get_product_by_id(product_id)
        if not product:
            return False
        self.db.delete(product)
        self.db.commit()
        return True

    def update_stock(self, product_id: int, new_stock: int) -> Optional[Product]:
        product = self.get_product_by_id(product_id)
        if not product:
            return None
        product.stock = new_stock
        # No commit here — called within larger transactions
        return product

    def get_top_products(
        self,
        date_from: datetime,
        date_to: datetime,
        limit: int = 5,
    ) -> list:
        """Top products by units sold in period (PAID + PARTIAL, excludes CANCELLED). Pure SQL GROUP BY."""
        from app.models.sale import Sale, SaleItem
        rows = (
            self.db.query(
                Product.id.label('product_id'),
                Product.name.label('product_name'),
                func.sum(SaleItem.quantity).label('units_sold'),
                func.sum(SaleItem.subtotal).label('revenue'),
            )
            .join(SaleItem, SaleItem.product_id == Product.id)
            .join(Sale, Sale.id == SaleItem.sale_id)
            .filter(
                Sale.status.in_(['PAID', 'PARTIAL']),
                Sale.sale_date >= date_from,
                Sale.sale_date <= date_to,
            )
            .group_by(Product.id, Product.name)
            .order_by(func.sum(SaleItem.quantity).desc())
            .limit(limit)
            .all()
        )
        return [
            {
                'product_id': r.product_id,
                'product_name': r.product_name,
                'units_sold': int(r.units_sold),
                'revenue': round(float(r.revenue), 2),
            }
            for r in rows
        ]
