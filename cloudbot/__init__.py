import json
import logging.config
import logging
import os

from .core import bot, connection, config, permissions, pluginmanager, events
from .util import botvars, bucket, formatting, hook, http, pyexec, textgen, timeformat, timesince, urlnorm, web

__all__ = ["core", "util", "bot", "connection", "config", "permissions", "pluginmanager", "events", "botvars", "bucket",
           "formatting", "hook", "http", "pyexec", "textgen", "timeformat", "timesince", "urlnorm", "web",
           "dev_mode_conf"]


def _setup():
    with open(os.path.abspath("config.json")) as config_file:
        json_conf = json.load(config_file)
    developer_mode = json_conf.get("developer_mode", {"reloading": False, "console_debug": False, "file_debug": True})

    if not "reloading" in developer_mode:
        developer_mode["reloading"] = False
    if not "console_debug" in developer_mode:
        developer_mode["console_debug"] = False
    if not "file_debug" in developer_mode:
        developer_mode["file_debug"] = True

    _logdir = os.path.join(os.path.abspath(os.path.curdir), "logs")

    if not os.path.exists(_logdir):
        os.makedirs(_logdir)

    dict_config = {
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
                "filename": os.path.join(_logdir, "bot.log")
            }
        },
        "loggers": {
            "cloudbot": {
                "level": "DEBUG",
                "handlers": ["console", "file"]
            }
        }
    }

    if developer_mode["console_debug"]:
        dict_config["handlers"]["console"]["level"] = "DEBUG"

    if developer_mode["file_debug"]:
        dict_config["handlers"]["debug_file"] = {
            "class": "logging.FileHandler",
            "formatter": "full",
            "level": "DEBUG",
            "filename": os.path.join(_logdir, "debug.log")
        }
        dict_config["loggers"]["cloudbot"]["handlers"].append("debug_file")

    logging.config.dictConfig(dict_config)

    return developer_mode


dev_mode_conf = _setup()