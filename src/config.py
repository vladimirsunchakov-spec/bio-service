from pydantic_settings import BaseSettings, SettingsConfigDict
from uuid import uuid4
from typing import Set, Optional, AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from contextvars import ContextVar
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from pydantic import PostgresDsn
from datetime import datetime, timezone
import logging
import logging.config
import json
from src.routers import bio

class Settings(BaseSettings):
    postgres_url: PostgresDsn

    redis_url: str = 'redis://localhost:6379/0'
    cache_ttl_seconds: int = 3600

    bio_service_url: str = 'http://localhost:8001'
    bio_client_timeout: float = 10.0

    retry_max_attempts: int = 3
    retry_wait_multiplier: int = 1
    retry_wait_min: int = 1
    retry_wait_max: int = 10

    non_retryable_statuses: Set[int] = {400, 401, 403, 404, 409, 422}
    retryable_statuses: Set[int] = {500, 502, 503, 504}
    success_statuses: Set[int] = {200, 201, 204}

    debug: bool = False

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra="ignore",
    )
settings = Settings()

engine = create_async_engine(
    str(settings.postgres_url),
    echo=False,
    future=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

_request_id_var: ContextVar[str] = ContextVar('_request_id', default="")

def get_request_id() -> str:
    return _request_id_var.get()

class RequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get('X-Request-Id', str(uuid4()))
        token = _request_id_var.set(request_id)
        try:
            response = await call_next(request)
            response.headers['X-Request-Id'] = request_id
            return response
        finally:
            _request_id_var.reset(token)

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        request_id = get_request_id()
        if request_id:
            log_data["request_id"] = request_id

        extra = getattr(record, "extra", {})
        if extra:
            log_data.update(extra)

        return json.dumps(log_data, ensure_ascii=False)

def setup_logging():
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "class": "src.config.JSONFormatter",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "level": "INFO",
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        },
    })

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Logging configured")
    yield
    await engine.dispose()
    logger.info("Database connection closed")

def register_routers(app: FastAPI) -> None:
    app.include_router(bio.router)

def get_app() -> FastAPI:
    app = FastAPI(
        title="Bio Service",
        description="Сервис для хранения дополнительной информации",
        version="1.0.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
        default_response_class=UJSONResponse,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestMiddleware)

    register_routers(app)
    return app
