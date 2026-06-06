"""Body measurement service."""

from sqlalchemy.orm import Session
from app.repositories.body_measurement_repository import BodyMeasurementRepository
from app.schemas.body_measurement import BodyMeasurementUpsert, BodyMeasurementRead


class BodyMeasurementService:

    def __init__(self, db: Session):
        self.repo = BodyMeasurementRepository(db)

    def get(self, member_id: int) -> BodyMeasurementRead | None:
        record = self.repo.get_by_member(member_id)
        if record is None:
            return None
        return BodyMeasurementRead.model_validate(record)

    def upsert(self, member_id: int, data: BodyMeasurementUpsert) -> BodyMeasurementRead:
        record = self.repo.upsert(member_id, data)
        return BodyMeasurementRead.model_validate(record)
