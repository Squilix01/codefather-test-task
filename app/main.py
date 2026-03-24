from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from app.api.v1.auth import router as auth_router
from app.api.v1.posts import router as posts_router
from app.api.v1.notifications import router as notifications_router

from app.tasks.broker import broker


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("підключаємося до RabbitMQ.")
    if not broker.is_worker_process:
        await broker.startup()
        
    yield 
    

    logger.info("відключаємося від RabbitMQ.")
    if not broker.is_worker_process:
        await broker.shutdown()

app = FastAPI(
    title="Mini Social API",
    lifespan=lifespan 
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()},
    )

app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(notifications_router)
