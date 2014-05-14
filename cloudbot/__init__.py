import logging.config
import os

from .core import bot, connection, config, permissions, pluginmanager, events
from .util import botvars, bucket, formatting, hook, http, pyexec, textgen, timeformat, timesince, urlnorm, web

__all__ = ["core", "util", "bot", "connection", "config", "permissions", "pluginmanager", "events", "botvars", "bucket",
           "formatting", "hook", "http", "pyexec", "textgen", "timeformat", "timesince", "urlnorm", "web"]

if not os.path.exists(os.path.join(".", "logs")):
    os.makedirs(os.path.join(".", "logs"))
logging.config.dictConfig({
    "version": 1,
    "formatters": {
        "brief": {
            "format": "[%(asctime)s][%(levelname)s] %(message)s",
            "datefmt": "%H:%M:%S"
        },
        "full": {
            "format": "[%(asctime)s][%(levelname)s] %(message)s",
            "datefmt": "%Y-%m-%d][%H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "brief",
            "level": "INFO",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "full",
            "level": "INFO",
            "filename": os.path.join(".", "logs", "bot.log")
        },
        "debug_file": {
            "class": "logging.FileHandler",
            "formatter": "full",
            "level": "DEBUG",
            "filename": os.path.join(".", "logs", "debug.log")
        }
    },
    "loggers": {
        "cloudbot": {
            "level": "DEBUG",
            "handlers": ["console", "file", "debug_file"]
        }
    }
})
