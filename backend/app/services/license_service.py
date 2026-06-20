"""License service — gym info, plan management, and module activation control."""

from datetime import datetime
from sqlalchemy.orm import Session

from app.core.licensing import MODULE_REGISTRY, PLAN_MODULES
from app.core.module_cache import refresh_gym
from app.repositories.license_repository import LicenseRepository
from app.schemas.gym import (
    GymRead, GymUpdate, LicenseRead, LicensePlanUpdate, LicenseValidityUpdate,
    ModuleStatusRead, ModuleToggle, GymLicensePanel,
)


class LicenseService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = LicenseRepository(db)

    def get_panel(self, gym_id: int) -> GymLicensePanel:
        gym = self.repo.get_gym(gym_id)
        if not gym:
            raise ValueError(f"Gimnasio {gym_id} no encontrado")
        license_ = self.repo.get_active_license(gym_id)
        modules = self.repo.get_modules(gym_id)

        module_statuses = [
            ModuleStatusRead(
                module_key=m.module_key,
                name=MODULE_REGISTRY.get(m.module_key, {}).get("name", m.module_key),
                active=m.active,
                source=m.source,
                activated_at=m.activated_at,
                deactivated_at=m.deactivated_at,
            )
            for m in modules
        ]

        return GymLicensePanel(
            gym=GymRead.model_validate(gym),
            license=LicenseRead.model_validate(license_) if license_ else None,
            modules=module_statuses,
        )

    def update_gym(self, gym_id: int, data: GymUpdate) -> GymRead:
        gym = self.repo.get_gym(gym_id)
        if not gym:
            raise ValueError(f"Gimnasio {gym_id} no encontrado")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(gym, field, value)
        self.db.commit()
        self.db.refresh(gym)
        return GymRead.model_validate(gym)

    def change_plan(self, gym_id: int, data: LicensePlanUpdate, user_id: int) -> LicenseRead:
        license_ = self.repo.get_active_license(gym_id)
        if not license_:
            raise ValueError("No hay licencia activa para este gimnasio")
        license_.plan_name = data.plan_name
        license_.updated_at = datetime.utcnow()

        # Update source for each module based on new plan coverage
        new_plan_modules = set(PLAN_MODULES.get(data.plan_name, []))
        for m in self.repo.get_modules(gym_id):
            m.source = "plan" if m.module_key in new_plan_modules else "addon"

        self.db.commit()
        self.db.refresh(license_)
        return LicenseRead.model_validate(license_)

    def update_validity(self, gym_id: int, data: LicenseValidityUpdate) -> LicenseRead:
        license_ = self.repo.get_active_license(gym_id)
        if not license_:
            raise ValueError("No hay licencia activa para este gimnasio")
        if data.valid_from is not None:
            license_.valid_from = data.valid_from
        license_.valid_until = data.valid_until  # None clears the expiry
        license_.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(license_)
        return LicenseRead.model_validate(license_)

    def toggle_module(
        self, gym_id: int, module_key: str, data: ModuleToggle, user_id: int
    ) -> ModuleStatusRead:
        if module_key not in MODULE_REGISTRY:
            raise ValueError(f"Módulo desconocido: {module_key}")
        module = self.repo.get_module(gym_id, module_key)
        if not module:
            raise ValueError(f"Módulo {module_key} no encontrado para el gimnasio {gym_id}")

        module.active = data.active
        if data.notes:
            module.notes = data.notes
        if data.active:
            module.activated_by = user_id
            module.activated_at = datetime.utcnow()
        else:
            module.deactivated_by = user_id
            module.deactivated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(module)

        # Invalidate and rebuild cache for this gym
        refresh_gym(gym_id, self.repo.get_modules(gym_id))

        return ModuleStatusRead(
            module_key=module.module_key,
            name=MODULE_REGISTRY.get(module_key, {}).get("name", module_key),
            active=module.active,
            source=module.source,
            activated_at=module.activated_at,
            deactivated_at=module.deactivated_at,
        )
