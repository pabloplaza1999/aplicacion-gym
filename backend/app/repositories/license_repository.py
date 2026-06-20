"""Repository for gym, license, and module data access."""

from sqlalchemy.orm import Session
from app.models.gym import Gym, GymLicense, GymModule


class LicenseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_gym(self, gym_id: int) -> Gym | None:
        return self.db.query(Gym).filter(Gym.id == gym_id).first()

    def get_active_license(self, gym_id: int) -> GymLicense | None:
        return (
            self.db.query(GymLicense)
            .filter(GymLicense.gym_id == gym_id, GymLicense.status == "active")
            .order_by(GymLicense.created_at.desc())
            .first()
        )

    def get_modules(self, gym_id: int) -> list[GymModule]:
        return self.db.query(GymModule).filter(GymModule.gym_id == gym_id).all()

    def get_module(self, gym_id: int, module_key: str) -> GymModule | None:
        return (
            self.db.query(GymModule)
            .filter(GymModule.gym_id == gym_id, GymModule.module_key == module_key)
            .first()
        )
