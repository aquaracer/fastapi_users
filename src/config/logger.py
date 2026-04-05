import os
import sys
from logging import INFO, Formatter, StreamHandler, getLogger
from logging.handlers import RotatingFileHandler

import structlog
from structlog.processors import (
    JSONRenderer,
    StackInfoRenderer,
    TimeStamper,
    add_log_level,
    format_exc_info,
)
from structlog.stdlib import LoggerFactory

LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/app.log")
LOG_MAX_BYTES = 10 * 1024 * 1024
LOG_BACKUP_COUNT = 5

def setup_logger():
    """
    Настройка глобального structlog для проекта FastAPI.
    Логи выводятся в stdout и в файл с ротацией.
    """

    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    stream_handler = StreamHandler(sys.stdout)
    stream_handler.setFormatter(Formatter("%(message)s"))
    file_handler = RotatingFileHandler(
        LOG_FILE_PATH,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setFormatter(Formatter("%(message)s"))
    root_logger = getLogger()
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(INFO)
    root_logger.propagate = False

    structlog.configure(
        processors=[
            add_log_level,
            TimeStamper(fmt="iso"),
            StackInfoRenderer(),
            format_exc_info,
            JSONRenderer()
        ],
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(INFO),
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger()

logger = setup_logger()