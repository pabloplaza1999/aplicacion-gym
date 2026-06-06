"""Payment API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.payment import PaymentCreate, PaymentRead, PaymentStatistics
from app.services.payment_service import PaymentService

router = APIRouter(tags=["payments"])


@router.post("/members/{member_id}/payments", response_model=PaymentRead, status_code=201)
def create_payment(
    member_id: int,
    payment_data: PaymentCreate,
    db: Session = Depends(get_db)
):
    """Create a new payment for a member.

    - **member_id**: Member ID
    - **payment_data**: Payment details (amount, method, optional membership_id)

    Returns:
    - 201: Payment created successfully
    - 400: Invalid payment method or amount
    """
    try:
        if payment_data.member_id != member_id:
            raise HTTPException(status_code=400, detail="Member ID mismatch")

        service = PaymentService(db)
        return service.create_payment(payment_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/members/{member_id}/payments", response_model=dict)
def get_member_payments(
    member_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all payments for a member.

    - **skip**: Number of payments to skip (pagination)
    - **limit**: Number of payments to return (max 100)

    Returns:
    - 200: List of payments with total count and total amount
    """
    service = PaymentService(db)
    result = service.get_member_payments(member_id, skip, limit)
    return result.model_dump()


# NOTE: Static routes MUST be registered before /payments/{payment_id}.
# FastAPI evaluates routes in registration order; if /{payment_id} comes first,
# "statistics", "method", "monthly" are captured as the path param and then
# fail integer conversion → 422 Unprocessable Entity.

@router.get("/payments/statistics/current-month", response_model=dict)
def get_current_month_statistics(
    db: Session = Depends(get_db)
):
    """Get payment statistics for the current month.

    Returns:
    - 200: Payment statistics for current month
    """
    service = PaymentService(db)
    result = service.get_current_month_statistics()
    return result.model_dump()


@router.get("/payments/statistics", response_model=dict)
def get_payment_statistics(
    db: Session = Depends(get_db)
):
    """Get payment statistics by method.

    Returns:
    - 200: Payment statistics including total, count, and breakdown by method
    """
    service = PaymentService(db)
    result = service.get_payment_statistics()
    return result.model_dump()


@router.get("/payments/method/{payment_method}", response_model=dict)
def get_payments_by_method(
    payment_method: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get payments by method.

    - **payment_method**: One of: cash, transfer, qr, nequi

    Returns:
    - 200: List of payments with specified method
    - 400: Invalid payment method
    """
    try:
        service = PaymentService(db)
        result = service.get_payments_by_method(payment_method, skip, limit)
        return result.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/payments/monthly/{year}/{month}", response_model=dict)
def get_monthly_payments(
    year: int,
    month: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get payments for a specific month.

    - **year**: Year (e.g., 2026)
    - **month**: Month (1-12)

    Returns:
    - 200: List of payments for the month
    - 400: Invalid month
    """
    try:
        service = PaymentService(db)
        result = service.get_monthly_payments(year, month, skip, limit)
        return result.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/payments/{payment_id}", response_model=PaymentRead)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    """Get a payment by ID.

    Returns:
    - 200: Payment details
    - 404: Payment not found
    """
    service = PaymentService(db)
    payment = service.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment



@router.delete("/payments/{payment_id}", status_code=200)
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
):
    """Delete a payment by ID."""
    service = PaymentService(db)
    deleted = service.delete_payment(payment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    return {"message": "Pago eliminado", "id": payment_id}

@router.get("/payments", response_model=dict)
def get_all_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all payments.

    - **skip**: Number of payments to skip (pagination)
    - **limit**: Number of payments to return (max 100)

    Returns:
    - 200: List of all payments with total count and total amount
    """
    service = PaymentService(db)
    result = service.get_all_payments(skip, limit)
    return result.model_dump()
