
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import config
from app.core.logging import setup_logging
from app.db.session import engine
from app.db.schema import Base
from app.api.v1.tasks import router as task


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


app = FastAPI(title=config.app_name)

@app.get("/")
def main():
    return {"message": "Welcome to Task Scheduler API. For documentation visit /docs for more information"}


app.include_router(task, prefix="/api/v1")
