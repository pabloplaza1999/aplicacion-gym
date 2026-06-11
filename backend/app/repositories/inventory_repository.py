"""Inventory movement repository."""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.inventory import InventoryMovement


class InventoryRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_movement(
        self,
        product_id: int,
        movement_type: str,
        quantity: int,
        stock_before: int,
        stock_after: int,
        note: Optional[str] = None,
        sale_id: Optional[int] = None,
    ) -> InventoryMovement:
        movement = InventoryMovement(
            product_id=product_id,
            type=movement_type,
            quantity=quantity,
            stock_before=stock_before,
            stock_after=stock_after,
            note=note,
            sale_id=sale_id,
        )
        self.db.add(movement)
        # No commit — caller manages the transaction
        return movement

    def get_movements_by_product(
        self, product_id: int, skip: int = 0, limit: int = 50
    ) -> List[InventoryMovement]:
        return (
            self.db.query(InventoryMovement)
            .filter(InventoryMovement.product_id == product_id)
            .order_by(InventoryMovement.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def product_has_movements(self, product_id: int) -> bool:
        return (
            self.db.query(InventoryMovement)
            .filter(InventoryMovement.product_id == product_id)
            .count()
        ) > 0

    def delete_movements_by_product(self, product_id: int) -> None:
        self.db.query(InventoryMovement).filter(
            InventoryMovement.product_id == product_id
        ).delete(synchronize_session=False)
