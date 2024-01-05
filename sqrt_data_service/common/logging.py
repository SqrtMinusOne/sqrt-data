# [[file:../../org/core-new.org::*Logging][Logging:1]]
import logging
import logging.config
import logging.handlers
import os
import sys

from sqrt_data_service.api import settings

__all__ = ["configure_logging"]


class ColorFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._colors = {
            "BLACK": "\033[0;30m",
            "RED": "\033[0;31m",
            "GREEN": "\033[0;32m",
            "YELLOW": "\033[0;33m",
            "BLUE": "\033[0;34m",
            "MAGENTA": "\033[0;35m",
            "CYAN": "\033[0;36m",
            "WHITE": "\033[0;37m",
            "RESET": "\033[0m",
        }
        self._level_colors = {
            "DEBUG": self._colors["BLUE"],
            "INFO": self._colors["GREEN"],
            "WARNING": self._colors["YELLOW"],
            "ERROR": self._colors["RED"],
            "CRITICAL": self._colors["MAGENTA"],
        }
        self._reset = "\033[0m"

    def format(self, record):
        record.level_color = self._level_colors.get(record.levelname, "")
        record.reset = self._reset
        return super().format(record)


def log_exceptions(type_, value, tb):
    logging.exception(value, exc_info=(type_, value, tb))

    sys.__excepthook__(type_, value, tb)


old_factory = logging.getLogRecordFactory()


def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    if scope := os.getenv('SCOPE'):
        record.scope = scope
    else:
        record.scope = 'unknown'
    return record


def configure_logging():
    if not os.path.exists("./logs"):
        os.mkdir("./logs")
    logging.config.dictConfig(settings.logging)
    logging.setLogRecordFactory(record_factory)
    sys.excepthook = log_exceptions
# Logging:1 ends here
