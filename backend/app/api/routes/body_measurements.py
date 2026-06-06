"""Body measurements API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.body_measurement import BodyMeasurementUpsert, BodyMeasurementRead
from app.services.body_measurement_service import BodyMeasurementService
from app.services.member_service import MemberService

router = APIRouter(prefix="/members", tags=["body_measurements"])


@router.get("/{member_id}/measurements", response_model=BodyMeasurementRead)
def get_measurements(member_id: int, db: Session = Depends(get_db)):
    svc = BodyMeasurementService(db)
    result = svc.get(member_id)
    if result is None:
        raise HTTPException(status_code=404, detail="No measurements found")
    return result


@router.put("/{member_id}/measurements", response_model=BodyMeasurementRead)
def upsert_measurements(
    member_id: int,
    data: BodyMeasurementUpsert,
    db: Session = Depends(get_db),
):
    # Verify member exists
    member_svc = MemberService(db)
    if not member_svc.get_member(member_id):
        raise HTTPException(status_code=404, detail="Member not found")
    return BodyMeasurementService(db).upsert(member_id, data)
