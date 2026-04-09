from typing import Optional

from sqlalchemy.orm import Session

from app.db.schema import User
from app.repository.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(db, User)

    def build_filters(self, search: Optional[str]):
        filters = []
        if search:
            filters.append(User.name.ilike(f"%{search}%"))
        return filters
