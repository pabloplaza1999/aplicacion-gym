"""Body measurement repository."""

from sqlalchemy.orm import Session
from app.models.body_measurement import BodyMeasurement
from app.schemas.body_measurement import BodyMeasurementUpsert
from datetime import datetime


class BodyMeasurementRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_member(self, member_id: int) -> BodyMeasurement | None:
        return self.db.query(BodyMeasurement)\
            .filter(BodyMeasurement.member_id == member_id).first()

    def upsert(self, member_id: int, data: BodyMeasurementUpsert) -> BodyMeasurement:
        record = self.get_by_member(member_id)
        if record is None:
            record = BodyMeasurement(member_id=member_id)
            self.db.add(record)
        for field, value in data.model_dump(exclude_unset=False).items():
            setattr(record, field, value)
        record.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(record)
        return record
