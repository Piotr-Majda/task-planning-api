from datetime import UTC, timedelta
import datetime
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import exc
from app.core.config import config
import jwt

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(UTC) + expires_delta
    else:
        expire = datetime.datetime.now(UTC) + timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINTUES
        )
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode,
        config.SECRET_KEY.get_secret_value(),
        algorithm=config.ALGORITHM
    )
    return encoded_jwt

def verify_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            config.SECRET_KEY.get_secret_value(),
            algorithms=[config.ALGORITHM],
            options={'require': ['exp', 'sub', 'role']},
        )
    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get('sub')


if '__main__' == __file__:
    print(hash_password('admin1234'))