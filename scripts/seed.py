from app.core.auth import hash_password
from app.db.schema import Base, User
from app.db.session import SessionLocal, engine
from app.domain.enums import UserRole
from app.repository.user_repository import UserRepository

def seed_dev_users():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        repo = UserRepository(db)
        if not repo.get_by_attr(name='admin'):
            admin = User(
                name='admin',
                role=UserRole.ADMIN,
                password_hashed=hash_password('admin1234')
                )
            repo.create(admin)
        if not repo.get_by_attr(name='user'):
            user = User(
                name='user',
                role=UserRole.USER,
                password_hashed=hash_password('user1234')
                )
            repo.create(user)
    finally:
        db.close()


if __name__ == "__main__": 
    seed_dev_users()
