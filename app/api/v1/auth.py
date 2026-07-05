from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.api.v1.dependencies import user_service_dep, _http_error
from app.exceptions.user_exceptions import InvalidPassword, UserNotFound
from app.models.users import Token


router = APIRouter(prefix='/auth')

@router.post("/token", response_model=Token)
def authenticate(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: user_service_dep,
):
    try:
        return service.auth(name=form.username, password=form.password)
    except (UserNotFound, InvalidPassword) as e:
        raise _http_error(
            status_code=401, 
            code='invalid_credentials', 
            detail="Invalid name or password",
            headers={"WWW-Authenticate": "Bearer"}
            )
