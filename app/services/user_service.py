from datetime import timedelta
from typing import List, Optional

from app.core.config import config
from app.core.auth import create_access_token, verify_access_token, verify_password
from app.db.schema import User
from app.domain.enums import OrderBy, SortBy, UserRole
from app.exceptions.user_exceptions import InvalidPassword, InvalidToken, NotAdminUser, UserNotFound
from app.models.users import Token, UserCreate, UserUpdate
from app.repository.user_repository import UserRepository


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    # ════════════════════════════════════════════════════════════
    # CRUD
    # ════════════════════════════════════════════════════════════

    def list(self, skip: int, limit: int, sort: SortBy, order: OrderBy, search: Optional[str])-> List[User]:
        filters = self._repo.build_filters(search)
        return self._repo.get_all(
            skip=skip, 
            limit=limit, 
            sort_by=sort, 
            order=order, 
            filters=filters
        )

    def get(self, id: int) -> User:
        user = self._repo.get_by_id(id)
        if not user:
            raise UserNotFound()
        return user

    def auth(self, name: str, password: str):
        user = self._repo.get_by_attr(name=name)
        if user is None:
            raise UserNotFound()
        if not verify_password(password, str(user.password_hashed)):
            raise InvalidPassword()
        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINTUES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")

    def get_user_by_token(self, token: str) -> User:
        user_id = verify_access_token(token)
        if user_id is None:
            raise InvalidToken()
        user_id = int(user_id)
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise UserNotFound()
        return user

    def get_admin_by_token(self, token: str) -> User:
        user = self.get_user_by_token(token)
        if user.role != UserRole.ADMIN:
            raise NotAdminUser()
        return user

    def create(self, project_create: UserCreate) -> User:
        params = project_create.model_dump(exclude_unset=True)
        password = params.pop('password')
        params['password_hashed'] = password
        user = User(**params)
        return self._repo.create(user)
    
    def update(self, id: int, params: UserUpdate) -> User:
        user = self.get(id)
        update_params = params.model_dump(exclude_none=True)
        if update_params.get('password') is not None:
            password = update_params.pop('password')
            update_params['password_hashed'] = password
        for name, value in update_params.items():
            setattr(user, name, value)
        
        return self._repo.update(user)

    def delete(self, id: int) -> None:
        user= self._repo.get_by_id(id)
        if not user:
            raise UserNotFound()
        self._repo.delete(user)
