
import asyncio
import time
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.concurrency import iterate_in_threadpool
from app.core.config import config
from app.core.logger import setup_logging
from app.db.session import engine, get_db
from app.db.schema import Base
from app.api.v1.tasks import router as task
from app.api.v1.projects import router as project
from app.api.v1.users import router as users
from app.api.v1.auth import router as auth
from app.exceptions.base_exceptions import BusinessException


logger = setup_logging(config.APP_NAME)


app = FastAPI(title=config.APP_NAME)
app.include_router(task, prefix="/api/v1")
app.include_router(project, prefix="/api/v1")
app.include_router(users, prefix="/api/v1")
app.include_router(auth, prefix="/api/v1")


if config.DEBUG is False:
    origins = [
    config.FRONTEND_URL,
]
else:
    origins = [
        'http://localhost',
        'http://127.0.0.1',
        config.FRONTEND_URL,
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def main():
    if config.DEBUG:
        return {"message": "Welcome to Task Scheduler API. For documentation visit /docs for more information"}
    else:
        return {"message": "Welcome to Task Scheduler API. to access API login via /api/v1/auth/token"}

@app.get("/health")
def health(db: Session = Depends(get_db)):
    def try_check_db_connection() -> bool:
        try:
            db.execute(text('SELECT 1'))
            return True
        except Exception:
            return False
    db_status = "up" if try_check_db_connection() else "down"
    app_status = 'healthy' if all([db_status == 'up']) else 'unhealthy'
    app_status_code = 200 if app_status == 'healthy' else 503
    return JSONResponse(content={"status": app_status, "checks": {'database': db_status}}, status_code=app_status_code)

@app.exception_handler(BusinessException)
async def buisnes_error_handler(
    request: Request, 
    exc: BusinessException
):
    return JSONResponse(
        status_code=400,
        content={
            'code': exc.code,
            'detail': exc.message
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException
):
    if isinstance(exc.detail, dict) and 'code' in exc.detail and 'detail' in exc.detail:
        content = exc.detail
    else:
        content = {
            "code": "http_error",
            "detail": exc.detail,
        }
    return JSONResponse(status_code=exc.status_code, content=content, headers=exc.headers)


@app.middleware('http')
async def handle_logging(request: Request, call_next):
    client_ip = request.client.host if request.client else 'unknown'
    method = request.method
    url = request.url.path
    if url.endswith('health'):
        response = await call_next(request)
        return response

    logger.info(f"Request: {method} {url} from {client_ip}")
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    status_code = response.status_code
    if config.DEBUG:
        res_body = [section async for section in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(res_body))

    logger.info(f"Response: {method} {url} returned {status_code} to {client_ip}")
    if config.DEBUG and res_body:
        res_body = res_body[0].decode()
        logger.info(f"Response body: \n{res_body}")
    return response
