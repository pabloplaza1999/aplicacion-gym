"""Inventory business logic."""

from typing import List
from sqlalchemy.orm import Session

from app.repositories.product_repository import ProductRepository
from app.repositories.inventory_repository import InventoryRepository
from app.schemas.inventory import InventoryMovementRead
from app.schemas.product import ProductRead


class InventoryService:

    def __init__(self, db: Session):
        self.product_repo = ProductRepository(db)
        self.inventory_repo = InventoryRepository(db)
        self.db = db

    def _enrich_movement(self, movement) -> dict:
        product = self.product_repo.get_product_by_id(movement.product_id)
        return {
            "id": movement.id,
            "product_id": movement.product_id,
            "product_name": product.name if product else None,
            "type": movement.type,
            "quantity": movement.quantity,
            "stock_before": movement.stock_before,
            "stock_after": movement.stock_after,
            "note": movement.note,
            "sale_id": movement.sale_id,
            "created_at": movement.created_at,
        }

    def _enrich_product(self, product) -> dict:
        cat = self.product_repo.get_category_by_id(product.category_id)
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

    def register_entry(self, product_id: int, quantity: int, note: str = None) -> InventoryMovementRead:
        product = self.product_repo.get_product_by_id(product_id)
        if not product:
            raise ValueError("Producto no encontrado.")
        if not product.is_active:
            raise ValueError("El producto está inactivo.")

        stock_before = product.stock
        stock_after = stock_before + quantity
        product.stock = stock_after

        movement = self.inventory_repo.create_movement(
            product_id=product_id,
            movement_type="entry",
            quantity=quantity,
            stock_before=stock_before,
            stock_after=stock_after,
            note=note,
        )
        self.db.commit()
        self.db.refresh(movement)
        return InventoryMovementRead(**self._enrich_movement(movement))

    def register_adjustment(self, product_id: int, quantity: int, note: str) -> InventoryMovementRead:
        product = self.product_repo.get_product_by_id(product_id)
        if not product:
            raise ValueError("Producto no encontrado.")

        stock_before = product.stock
        stock_after = stock_before + quantity
        if stock_after < 0:
            raise ValueError(
                f"El ajuste dejaría el stock en {stock_after}. El stock no puede ser negativo."
            )

        product.stock = stock_after
        movement = self.inventory_repo.create_movement(
            product_id=product_id,
            movement_type="adjustment",
            quantity=quantity,
            stock_before=stock_before,
            stock_after=stock_after,
            note=note,
        )
        self.db.commit()
        self.db.refresh(movement)
        return InventoryMovementRead(**self._enrich_movement(movement))

    def get_movements(self, product_id: int, skip: int = 0, limit: int = 50) -> List[InventoryMovementRead]:
        if not self.product_repo.get_product_by_id(product_id):
            raise ValueError("Producto no encontrado.")
        movements = self.inventory_repo.get_movements_by_product(product_id, skip=skip, limit=limit)
        return [InventoryMovementRead(**self._enrich_movement(m)) for m in movements]

    def get_low_stock_products(self) -> List[ProductRead]:
        products = self.product_repo.get_products(low_stock=True, active_only=True)
        return [ProductRead(**self._enrich_product(p)) for p in products]
