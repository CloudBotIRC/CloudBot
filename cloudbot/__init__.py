import logging
import sys

from .core import bot, connection, config, permissions, plugins
from .util import botvars, bucket, formatting, hook, http, pyexec, textgen, timeformat, timesince, urlnorm, web

__all__ = ["core", "util", "bot", "connection", "config", "permissions", "plugins", "botvars", "bucket", "formatting",
           "hook", "http", "pyexec", "textgen", "timeformat", "timesince", "urlnorm", "web"]


def _setup_logger():
    logger = logging.getLogger("cloudbot")

    logger.setLevel(logging.DEBUG)

    # add a file handler
    file_handler = logging.FileHandler("bot.log")
    file_handler.setLevel(logging.INFO)

    # add debug file handler
    debug_file_handler = logging.FileHandler("debug.log")
    debug_file_handler.setLevel(logging.DEBUG)

    # stdout handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # create a formatter and set the formatter for the handler.
    file_formatter = logging.Formatter('{asctime}[{levelname}] {message}', '[%Y-%m-%d][%H:%M:%S]', '{')
    console_formatter = logging.Formatter('{asctime}[{levelname}] {message}', '[%H:%M:%S]', '{')
    file_handler.setFormatter(file_formatter)
    debug_file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    # add the Handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(debug_file_handler)
    logger.addHandler(console_handler)


_setup_logger()
