
from fastapi import FastAPI
from app.core.config import config
from app.core.logging import setup_logging
from app.db.schema import Base, engine
from app.api.v1.tasks import router as task


setup_logging()
Base.metadata.create_all(bind=engine)

app = FastAPI(title=config.app_name)

@app.get("/")
def main():
    return "Welcome"

app.include_router(task, prefix="/api")
