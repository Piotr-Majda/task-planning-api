from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from app.db.schema import Base

DATABSE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABSE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autoflush=False)
Base.metadata.create_all(bind=engine)