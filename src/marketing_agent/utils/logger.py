import logging
from logging.handlers import RotatingFileHandler

from pathlib import Path

from marketing_agent.config.settings import settings


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)

LOG_DIR = PROJECT_ROOT / "logs"

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

LOG_FILE = (
    LOG_DIR
    / "marketing_agent.log"
)


def get_logger(
    name: str,
) -> logging.Logger:
    logger = logging.getLogger(name)

    logger.setLevel(
        settings.log_level
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    )

    has_stream_handler = any(
        isinstance(
            handler,
            logging.StreamHandler,
        )
        and not isinstance(
            handler,
            logging.FileHandler,
        )
        for handler in logger.handlers
    )

    if not has_stream_handler:
        stream_handler = (
            logging.StreamHandler()
        )

        stream_handler.setFormatter(
            formatter
        )

        logger.addHandler(
            stream_handler
        )

    has_file_handler = any(
        isinstance(
            handler,
            logging.FileHandler,
        )
        for handler in logger.handlers
    )

    if not has_file_handler:
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )

        file_handler.setFormatter(
            formatter
        )

        logger.addHandler(
            file_handler
        )

    logger.propagate = False

    return logger