"""AdminUser repository — CRUD for the single admin user."""

from sqlalchemy.orm import Session
from app.models.admin_user import AdminUser


class AdminUserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_first(self) -> AdminUser | None:
        return self.db.query(AdminUser).first()

    def get_by_username(self, username: str) -> AdminUser | None:
        return self.db.query(AdminUser).filter(AdminUser.username == username).first()

    def create(self, username: str, hashed_password: str) -> AdminUser:
        user = AdminUser(username=username, hashed_password=hashed_password, is_temporary=True)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user: AdminUser, hashed_password: str, is_temporary: bool = False) -> AdminUser:
        user.hashed_password = hashed_password
        user.is_temporary = is_temporary
        self.db.commit()
        self.db.refresh(user)
        return user
