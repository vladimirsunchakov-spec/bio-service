import logging
import logging.config
import json
from datetime import datetime, timezone
from typing import Optional, Dict
from pydantic import BaseModel
from ..middleware.request_id import get_request_id

class LogSchema(BaseModel):
    timestamp: str
    level: str
    message: str
    module: str
    function: str
    line: int
    request_id: Optional[str] = None
    entity_id: Optional[str] = None
    user_id: Optional[str] = None
    author_id: Optional[str] = None
    country_id: Optional[str] = None

class FormatterConfig(BaseModel):
    class_name: str

class HandlerConfig(BaseModel):
    class_name: str
    formatter: str
    level: str

class RootConfig(BaseModel):
    level: str
    handlers: list[str]

class LoggingConfig(BaseModel):
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: Dict[str, FormatterConfig]
    handlers: Dict[str, HandlerConfig]
    root: RootConfig

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = LogSchema(
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=record.levelname,
            message=record.getMessage(),
            module=record.module,
            function=record.funcName,
            line=record.lineno,
            request_id=getattr(record, 'request_id', None),
            entity_id=getattr(record, 'entity_id', None),
            user_id=getattr(record, 'user_id', None)
        )

        extra_fields = getattr(record, 'extra', {})
        if extra_fields:
            for key, value in extra_fields.items():
                if hasattr(log_data, key):
                    setattr(log_data, key, value)

        return log_data.model_dump_json()

    def setup_logging():
        config = LoggingConfig(
            version=1,
            disable_existing_loggers=False,
            formatters={
                "json": FormatterConfig(
                    class_name="src.core.logger.JSONFormatter",
                ),
            },
            handlers={
                "console": HandlerConfig(
                    class_name="logging.StreamHandler",
                    formatter="json",
                    level="INFO"
                ),
            },
            root=RootConfig(
                level="INFO",
                handlers=["console"],
            ),
        )
        logging.config.dictConfig(config.model_dump())