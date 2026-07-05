from datetime import datetime
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import hash_password
from app.db.schema import Base, User
from app.db.session import get_db
from app.api.v1.dependencies import get_current_admin_user, get_current_user
from app.domain.enums import UserRole
from app.main import app
from app.models.users import UserCreate, UserRead


@pytest.fixture(scope="function")
def engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine

@pytest.fixture(scope="function")
def db(engine):
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()

@pytest.fixture(scope='function')
def admin_user() -> UserCreate:
    return UserCreate(name='admin', role=UserRole.ADMIN, password='admin1234')


@pytest.fixture(scope='function')
def create_admin_user(db: Session, admin_user: UserCreate) -> User:
    data = UserCreate.model_dump(admin_user, exclude_unset=True)
    password = data.pop('password')
    data['password_hashed'] = hash_password(password)
    user = User(**data)
    with db as session:
        session.add(user)
        session.commit()
        session.flush()
        return user

@pytest.fixture(scope='function')
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    def override_get_current_user():
        return UserRead(id=1, name='admin', role='admin', created_at=datetime.now(), updated_at=datetime.now())

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_admin_user] = override_get_current_user

    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope='function')
def bear_client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()
