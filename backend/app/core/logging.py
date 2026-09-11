import json
import logging
from datetime import UTC, datetime


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        data = {
            "time": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("request_id", "status", "duration_ms", "error_type"):
            if hasattr(record, key):
                data[key] = getattr(record, key)
        return json.dumps(data, ensure_ascii=False)


def configure_logging(level: str) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.getLogger("producto").handlers = [handler]
    logging.getLogger("producto").setLevel(level)
    logging.getLogger("producto").propagate = False
