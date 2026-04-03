
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.config import config
from app.core.logging import setup_logging
from app.db.session import engine
from app.db.schema import Base
from app.api.v1.tasks import router as task
from app.exceptions.base_exceptions import BuisnesException


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


app = FastAPI(title=config.app_name)
app.include_router(task, prefix="/api/v1")

@app.get("/")
def main():
    return {"message": "Welcome to Task Scheduler API. For documentation visit /docs for more information"}

@app.exception_handler(BuisnesException)
async def buisnes_error_handler(
    request: Request, 
    exc: BuisnesException
):
    return JSONResponse(
        status_code=400,
        content={
            'detail': exc.message
        }
    )
