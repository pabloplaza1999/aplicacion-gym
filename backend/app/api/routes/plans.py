"""Plans API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.models.plan import Plan

router = APIRouter(tags=["plans"])


@router.get("/plans", response_model=List[dict])
def get_plans(db: Session = Depends(get_db)):
    """Get all available plans."""
    plans = db.query(Plan).order_by(Plan.price).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "duration_days": p.duration_days,
            "plan_type": p.plan_type,
            "entry_count": p.entry_count,
        }
        for p in plans
    ]
