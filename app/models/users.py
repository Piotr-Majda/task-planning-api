from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, BeforeValidator, Field, field_validator, model_validator

from app.core.auth import hash_password
from app.domain.constants import NAME_MAX_LEN, PASSWORD_MAX_LEN, PASSWORD_MIN_LEN
from app.domain.enums import UserRole


def ensure_password_format(password: str) -> str:
    if len(password) < PASSWORD_MIN_LEN:
        raise ValueError(f"Password lenght to short min {PASSWORD_MIN_LEN} char")
    elif len(password) > PASSWORD_MAX_LEN:
        raise ValueError(f"Password lenght to wide max {PASSWORD_MAX_LEN} char")
    return hash_password(password)

def ensure_role_format(role: str) -> str:
    try:
       return UserRole(role)
    except ValueError as err:
        raise ValueError("User role format incorrect")

class UserCreate(BaseModel):
    name: str = Field(max_length=NAME_MAX_LEN)
    password: Annotated[str, BeforeValidator(ensure_password_format)]
    role: Annotated[str, BeforeValidator(ensure_role_format)] = UserRole.USER


class UserRead(BaseModel):
    id: int
    name: str
    role: str
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    name: Optional[str] = Field(max_length=NAME_MAX_LEN, default=None)
    password: Annotated[Optional[str], BeforeValidator(ensure_password_format)] = None
    role: Annotated[Optional[str], BeforeValidator(ensure_role_format)] = None


class Token(BaseModel):
    access_token: str
    token_type: str