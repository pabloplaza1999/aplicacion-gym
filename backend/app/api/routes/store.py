"""Store routes — categories, products, inventory, sales, customers, cartera."""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.member import Member
from app.schemas.product import CategoryCreate, CategoryUpdate, CategoryRead, ProductCreate, ProductUpdate, ProductRead
from app.schemas.inventory import InventoryEntryCreate, InventoryAdjustmentCreate, InventoryMovementRead
from app.schemas.sale import SaleCreate, SaleRead, SaleListResponse, CarteraResponse, StoreReportResponse
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerRead
from app.schemas.member import MemberCreate, MemberUpdate
from app.schemas.credit_payment import CreditPaymentCreate, CreditPaymentRead
from app.services.product_service import ProductService
from app.services.inventory_service import InventoryService
from app.services.sale_service import SaleService, InsufficientStockError, CannotCancelPartialSaleError
from app.services.member_service import MemberService, DuplicateDocumentError
from app.services.credit_payment_service import CreditPaymentService, CannotPayCancelledSaleError, ExceedsBalanceError
from app.repositories.member_repository import MemberRepository

router = APIRouter(prefix="/store", tags=["store"])


# ── Categories ────────────────────────────────────────────────────────────────

@router.get("/categories", response_model=list[CategoryRead])
def get_categories(active_only: bool = False, db: Session = Depends(get_db)):
    return ProductService(db).get_categories(active_only=active_only)


@router.post("/categories", response_model=CategoryRead, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    try:
        return ProductService(db).create_category(name=data.name, description=data.description)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.put("/categories/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    try:
        return ProductService(db).update_category(category_id, **data.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.patch("/categories/{category_id}/active", response_model=CategoryRead)
def toggle_category(category_id: int, is_active: bool, db: Session = Depends(get_db)):
    try:
        return ProductService(db).set_category_active(category_id, is_active)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))


@router.delete("/categories/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    try:
        ProductService(db).delete_category(category_id)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


# ── Products ──────────────────────────────────────────────────────────────────

@router.get("/products", response_model=dict)
def get_products(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    low_stock: bool = False,
    active_only: bool = False,
    skip: int = 0,
    limit: int = Query(100, le=200),
    db: Session = Depends(get_db),
):
    return ProductService(db).get_products(
        search=search, category_id=category_id,
        low_stock=low_stock, active_only=active_only,
        skip=skip, limit=limit,
    )


@router.post("/products", response_model=ProductRead, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    try:
        return ProductService(db).create_product(
            category_id=data.category_id, name=data.name, description=data.description,
            price=data.price, cost=data.cost, stock=data.stock, min_stock=data.min_stock,
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    try:
        return ProductService(db).get_product(product_id)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))


@router.put("/products/{product_id}", response_model=ProductRead)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    try:
        return ProductService(db).update_product(product_id, **data.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.patch("/products/{product_id}/active", response_model=ProductRead)
def toggle_product(product_id: int, is_active: bool, db: Session = Depends(get_db)):
    try:
        return ProductService(db).set_product_active(product_id, is_active)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))


@router.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    try:
        ProductService(db).delete_product(product_id)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.post("/products/bulk-delete", response_model=dict)
def bulk_delete_products(product_ids: list[int], db: Session = Depends(get_db)):
    return ProductService(db).delete_products_bulk(product_ids)


# ── Inventory ─────────────────────────────────────────────────────────────────

@router.post("/products/{product_id}/inventory/entry", response_model=InventoryMovementRead)
def register_entry(product_id: int, data: InventoryEntryCreate, db: Session = Depends(get_db)):
    try:
        return InventoryService(db).register_entry(product_id=product_id, quantity=data.quantity, note=data.note)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.post("/products/{product_id}/inventory/adjustment", response_model=InventoryMovementRead)
def register_adjustment(product_id: int, data: InventoryAdjustmentCreate, db: Session = Depends(get_db)):
    try:
        return InventoryService(db).register_adjustment(product_id=product_id, quantity=data.quantity, note=data.note)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.get("/products/{product_id}/inventory/movements", response_model=list[InventoryMovementRead])
def get_movements(
    product_id: int,
    skip: int = 0,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    try:
        return InventoryService(db).get_movements(product_id, skip=skip, limit=limit)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))


@router.get("/inventory/low-stock", response_model=list[ProductRead])
def get_low_stock(db: Session = Depends(get_db)):
    return InventoryService(db).get_low_stock_products()


# ── Customers → Member aliases ────────────────────────────────────────────────

def _member_as_customer(member, debt_total: float = 0.0) -> CustomerRead:
    """Map a Member ORM or MemberRead to CustomerRead for backward-compatible store responses."""
    return CustomerRead(
        id=member.id,
        name=member.full_name,
        document=member.document,
        phone=member.phone,
        email=member.email,
        notes=member.notes,
        member_id=member.id,
        member_name=member.full_name,
        debt_total=debt_total,
        created_at=member.registration_date,
    )


@router.get("/customers", response_model=list[CustomerRead])
def get_customers(
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    members = MemberService(db).get_members_for_store(q=q, skip=skip, limit=limit)
    repo = MemberRepository(db)
    return [_member_as_customer(m, repo.get_debt_total(m.id)) for m in members]


@router.post("/customers", response_model=CustomerRead, status_code=201)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    if not data.phone:
        raise HTTPException(400, detail="El teléfono es obligatorio para crear un cliente.")
    svc = MemberService(db)
    repo = MemberRepository(db)
    try:
        member_read = svc.create_member(MemberCreate(
            full_name=data.name,
            phone=data.phone,
            document=data.document,
            email=data.email,
            notes=data.notes,
        ))
    except DuplicateDocumentError:
        raise HTTPException(409, detail="Ya existe un cliente con ese número de documento.")
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    return _member_as_customer(member_read, repo.get_debt_total(member_read.id))


@router.post("/customers/from-member/{member_id}", response_model=CustomerRead, status_code=200)
def customer_from_member(member_id: int, db: Session = Depends(get_db)):
    """Alias kept for backward compat — returns the member directly as CustomerRead."""
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(404, detail="Miembro no encontrado.")
    repo = MemberRepository(db)
    return _member_as_customer(member, repo.get_debt_total(member.id))


@router.get("/customers/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == customer_id).first()
    if not member:
        raise HTTPException(404, detail="Cliente no encontrado.")
    repo = MemberRepository(db)
    return _member_as_customer(member, repo.get_debt_total(member.id))


@router.put("/customers/{customer_id}", response_model=CustomerRead)
def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db)):
    svc = MemberService(db)
    repo = MemberRepository(db)
    update_data = MemberUpdate(
        full_name=data.name,
        phone=data.phone,
        document=data.document,
        email=data.email,
        notes=data.notes,
    )
    result = svc.update_member(customer_id, update_data)
    if not result:
        raise HTTPException(404, detail="Cliente no encontrado.")
    member = db.query(Member).filter(Member.id == customer_id).first()
    return _member_as_customer(member, repo.get_debt_total(member.id))


@router.delete("/customers/{customer_id}", status_code=204)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    try:
        MemberService(db).delete_customer_from_store(customer_id)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


# ── Sales ─────────────────────────────────────────────────────────────────────

@router.post("/sales/purge-orphaned", response_model=dict)
def purge_orphaned_sales(db: Session = Depends(get_db)):
    deleted = SaleService(db).purge_orphaned_cancelled()
    return {"deleted": deleted}


@router.post("/sales", response_model=SaleRead, status_code=201)
def create_sale(data: SaleCreate, db: Session = Depends(get_db)):
    try:
        return SaleService(db).create_sale(data)
    except InsufficientStockError as e:
        raise HTTPException(409, detail=str(e))
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.get("/sales", response_model=SaleListResponse)
def get_sales(
    customer_id: Optional[int] = None,
    status: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    return SaleService(db).get_sales(
        customer_id=customer_id, status=status,
        from_date=from_date, to_date=to_date,
        skip=skip, limit=limit,
    )


@router.get("/sales/{sale_id}", response_model=SaleRead)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    try:
        return SaleService(db).get_sale(sale_id)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))


@router.post("/sales/{sale_id}/cancel", response_model=SaleRead)
def cancel_sale(sale_id: int, note: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        return SaleService(db).cancel_sale(sale_id, note=note)
    except CannotCancelPartialSaleError as e:
        raise HTTPException(400, detail=str(e))
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


# ── Credit payments (abonos) ──────────────────────────────────────────────────

@router.post("/sales/{sale_id}/payments", response_model=CreditPaymentRead, status_code=201)
def register_payment(sale_id: int, data: CreditPaymentCreate, db: Session = Depends(get_db)):
    try:
        return CreditPaymentService(db).register_payment(sale_id, data)
    except (CannotPayCancelledSaleError, ExceedsBalanceError) as e:
        raise HTTPException(400, detail=str(e))
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.get("/sales/{sale_id}/payments", response_model=list[CreditPaymentRead])
def get_payments(sale_id: int, db: Session = Depends(get_db)):
    try:
        return CreditPaymentService(db).get_payments_by_sale(sale_id)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))


# ── Cartera ───────────────────────────────────────────────────────────────────

@router.get("/cartera", response_model=CarteraResponse)
def get_cartera(
    status: Optional[str] = Query(None, pattern="^(PENDING|PARTIAL)$"),
    skip: int = 0,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    return SaleService(db).get_cartera(status_filter=status, skip=skip, limit=limit)


# ── Reports (Fase C) ──────────────────────────────────────────────────────────

@router.get("/reports", response_model=StoreReportResponse)
def get_store_reports(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    now = datetime.utcnow()
    resolved_from = date_from or now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    resolved_to = date_to or now
    return SaleService(db).get_store_report(resolved_from, resolved_to)
