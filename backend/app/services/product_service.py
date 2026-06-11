"""Product and category business logic."""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.repositories.product_repository import ProductRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.sale_repository import SaleRepository
from app.schemas.product import CategoryRead, ProductRead


class ProductService:

    def __init__(self, db: Session):
        self.repo = ProductRepository(db)
        self.inventory_repo = InventoryRepository(db)
        self.sale_repo = SaleRepository(db)
        self.db = db

    def _enrich_product(self, product) -> dict:
        cat = self.repo.get_category_by_id(product.category_id)
        return {
            "id": product.id,
            "category_id": product.category_id,
            "category_name": cat.name if cat else None,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "cost": product.cost,
            "stock": product.stock,
            "min_stock": product.min_stock,
            "is_active": product.is_active,
            "is_low_stock": product.stock <= product.min_stock,
            "created_at": product.created_at,
        }

    # ── Categories ────────────────────────────────────────────────────────────

    def get_categories(self, active_only: bool = False) -> List[CategoryRead]:
        cats = self.repo.get_categories(active_only=active_only)
        return [CategoryRead.from_orm(c) for c in cats]

    def create_category(self, name: str, description: Optional[str] = None) -> CategoryRead:
        if self.repo.get_category_by_name(name):
            raise ValueError(f"Ya existe una categoria con el nombre '{name}'.")
        cat = self.repo.create_category(name=name, description=description)
        return CategoryRead.from_orm(cat)

    def update_category(self, category_id: int, **kwargs) -> CategoryRead:
        if not self.repo.get_category_by_id(category_id):
            raise ValueError("Categoria no encontrada.")
        if "name" in kwargs and kwargs["name"]:
            existing = self.repo.get_category_by_name(kwargs["name"])
            if existing and existing.id != category_id:
                raise ValueError(f"Ya existe una categoria con el nombre '{kwargs['name']}'.")
        cat = self.repo.update_category(category_id, **kwargs)
        return CategoryRead.from_orm(cat)

    def set_category_active(self, category_id: int, is_active: bool) -> CategoryRead:
        cat = self.repo.set_category_active(category_id, is_active)
        if not cat:
            raise ValueError("Categoria no encontrada.")
        return CategoryRead.from_orm(cat)

    def delete_category(self, category_id: int) -> None:
        if not self.repo.get_category_by_id(category_id):
            raise ValueError("Categoria no encontrada.")
        if self.repo.category_has_products(category_id):
            raise ValueError("No se puede eliminar una categoria con productos asociados.")
        self.repo.delete_category(category_id)

    # ── Products ──────────────────────────────────────────────────────────────

    def get_products(
        self,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        low_stock: bool = False,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> dict:
        products = self.repo.get_products(
            search=search, category_id=category_id,
            low_stock=low_stock, active_only=active_only,
            skip=skip, limit=limit,
        )
        total = self.repo.count_products(
            search=search, category_id=category_id,
            low_stock=low_stock, active_only=active_only,
        )
        return {"total": total, "items": [ProductRead(**self._enrich_product(p)) for p in products]}

    def get_product(self, product_id: int) -> ProductRead:
        product = self.repo.get_product_by_id(product_id)
        if not product:
            raise ValueError("Producto no encontrado.")
        return ProductRead(**self._enrich_product(product))

    def create_product(
        self,
        category_id: int,
        name: str,
        description: Optional[str],
        price: float,
        cost: Optional[float],
        stock: int,
        min_stock: int,
    ) -> ProductRead:
        if not self.repo.get_category_by_id(category_id):
            raise ValueError("Categoria no encontrada.")
        if self.repo.get_product_by_name(name):
            raise ValueError(f"Ya existe un producto con el nombre '{name}'.")
        product = self.repo.create_product(
            category_id=category_id, name=name, description=description,
            price=price, cost=cost, stock=stock, min_stock=min_stock,
        )
        if stock > 0:
            self.inventory_repo.create_movement(
                product_id=product.id,
                movement_type="entry",
                quantity=stock,
                stock_before=0,
                stock_after=stock,
                note="Inventario inicial",
            )
            self.db.commit()
        return ProductRead(**self._enrich_product(product))

    def update_product(self, product_id: int, **kwargs) -> ProductRead:
        if not self.repo.get_product_by_id(product_id):
            raise ValueError("Producto no encontrado.")
        if "name" in kwargs and kwargs["name"]:
            existing = self.repo.get_product_by_name(kwargs["name"])
            if existing and existing.id != product_id:
                raise ValueError(f"Ya existe un producto con el nombre '{kwargs['name']}'.")
        product = self.repo.update_product(product_id, **kwargs)
        return ProductRead(**self._enrich_product(product))

    def set_product_active(self, product_id: int, is_active: bool) -> ProductRead:
        product = self.repo.set_product_active(product_id, is_active)
        if not product:
            raise ValueError("Producto no encontrado.")
        return ProductRead(**self._enrich_product(product))

    def delete_product(self, product_id: int) -> None:
        if not self.repo.get_product_by_id(product_id):
            raise ValueError("Producto no encontrado.")
        # Collect affected sale ids before deleting items
        sale_ids = self.sale_repo.get_sale_ids_by_product(product_id)
        # Cascade: remove sale items, then sales that become empty, then movements
        self.sale_repo.delete_items_by_product(product_id)
        self.sale_repo.delete_empty_sales(sale_ids)
        self.inventory_repo.delete_movements_by_product(product_id)
        self.repo.delete_product(product_id)

    def delete_products_bulk(self, product_ids: List[int]) -> dict:
        """Delete multiple products. Returns counts of deleted and blocked."""
        deleted = []
        blocked = []
        for pid in product_ids:
            try:
                self.delete_product(pid)
                deleted.append(pid)
            except ValueError as e:
                blocked.append({"id": pid, "reason": str(e)})
        return {"deleted": deleted, "blocked": blocked}
