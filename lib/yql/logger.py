"""Logging for Python YQL."""

import os
import logging
import logging.handlers


LOG_DIRECTORY_DEFAULT = os.path.join(os.path.dirname(__file__), "../logs")
LOG_DIRECTORY = os.environ.get("YQL_LOG_DIR", LOG_DIRECTORY_DEFAULT)
LOG_LEVELS = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.ERROR,
              'critical': logging.CRITICAL}

LOG_LEVEL = os.environ.get("YQL_LOGGING_LEVEL", 'debug')
LOG_FILENAME = os.path.join(LOG_DIRECTORY, "python-yql.log")
MAX_BYTES = 1024 * 1024

log_level = LOG_LEVELS.get(LOG_LEVEL)
yql_logger = logging.getLogger("python-yql")
yql_logger.setLevel(LOG_LEVELS.get(LOG_LEVEL))


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


def get_logger():
    """Set-upt the logger if enabled or fallback to NullHandler."""
    if os.environ.get("YQL_LOGGING", False):
        if not os.path.exists(LOG_DIRECTORY):
            os.mkdir(LOG_DIRECTORY)
        log_handler = logging.handlers.RotatingFileHandler(
                                LOG_FILENAME, maxBytes=MAX_BYTES,
                                backupCount=5)
        formatter = logging.Formatter(
                        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_handler.setFormatter(formatter)
    else:
        log_handler = NullHandler()
    yql_logger.addHandler(log_handler)
    return yql_logger
