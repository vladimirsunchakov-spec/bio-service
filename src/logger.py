import logging
import logging.config
import json
from datetime import datetime, timezone
from typing import Optional, Dict


logger = logging.getLogger(__name__)

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
        request_id = getattr(record, "request_id", None)
        if request_id:
            log_data["request_id"] = request_id
        extra = getattr(record, 'extra', {})
        if extra:
            log_data.update(extra)

        return json.dumps(log_data, ensure_ascii=False)

def setup_logging():
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "class": "src.core.logger.JSONFormatter",
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
