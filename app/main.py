
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.config import config
from app.core.logging import setup_logging
from app.db.session import engine
from app.db.schema import Base
from app.api.v1.tasks import router as task
from app.api.v1.projects import router as project
from app.exceptions.base_exceptions import BusinessException


logger = setup_logging(config.app_name)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


app = FastAPI(title=config.app_name)
app.include_router(task, prefix="/api/v1")
app.include_router(project, prefix="/api/v1")

@app.get("/")
def main():
    return {"message": "Welcome to Task Scheduler API. For documentation visit /docs for more information"}

@app.exception_handler(BusinessException)
async def buisnes_error_handler(
    request: Request, 
    exc: BusinessException
):
    return JSONResponse(
        status_code=400,
        content={
            'detail': exc.message
        }
    )

@app.middleware('http')
async def handle_logging(request: Request, call_next):
    client_ip = request.client.host if request.client else 'unknown'
    method = request.method
    url = request.url.path

    logger.info(f"Request: {method} {url} from {client_ip}")
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    status_code = response.status_code
    logger.info(f"Response: {method} {url} returned {status_code} to {client_ip}")
    return response
