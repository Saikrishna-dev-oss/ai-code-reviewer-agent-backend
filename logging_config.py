"""Application logging setup.

Uses Python's built-in logging framework and stores logs in SQLite through a
custom handler. This satisfies both: logging framework + database logging.
"""

from __future__ import annotations

import logging

from database import insert_api_log


class SQLiteLogHandler(logging.Handler):
    """A small logging handler that writes log records into SQLite."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            insert_api_log(
                level=record.levelname,
                logger_name=record.name,
                message=self.format(record),
                method=getattr(record, "method", None),
                path=getattr(record, "path", None),
                status_code=getattr(record, "status_code", None),
            )
        except Exception:
            # Never crash the API because logging failed.
            self.handleError(record)


def configure_logging() -> logging.Logger:
    """Configure and return the project logger."""
    logger = logging.getLogger("ai_code_reviewer")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if not any(isinstance(handler, SQLiteLogHandler) for handler in logger.handlers):
        database_handler = SQLiteLogHandler()
        database_handler.setFormatter(formatter)
        logger.addHandler(database_handler)

    return logger
