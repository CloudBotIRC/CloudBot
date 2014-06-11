import json
import logging.config
import logging
import os

from .core import bot, connection, config, permissions, pluginmanager, events
from .util import botvars, bucket, formatting, hook, http, textgen, timeformat, timesince, urlnorm, web

__version__ = "0.1.1.dev0"

__all__ = ["core", "util", "bot", "connection", "config", "permissions", "pluginmanager", "events", "botvars", "bucket",
           "formatting", "hook", "http", "textgen", "timeformat", "timesince", "urlnorm", "web", "dev_mode"]


def _setup():
    default_developer_mode = {"plugin_reloading": False, "config_reloading": True,
                              "console_debug": False, "file_debug": True}
    if os.path.exists(os.path.abspath("config.json")):
        with open(os.path.abspath("config.json")) as config_file:
            json_conf = json.load(config_file)
        developer_mode = json_conf.get("developer_mode", default_developer_mode)
    else:
        developer_mode = default_developer_mode

    if not "config_reloading" in developer_mode:
        developer_mode["config_reloading"] = default_developer_mode["config_reloading"]
    if not "plugin_reloading" in developer_mode:
        developer_mode["plugin_reloading"] = default_developer_mode["plugin_reloading"]
    if not "console_debug" in developer_mode:
        developer_mode["console_debug"] = default_developer_mode["console_debug"]
    if not "file_debug" in developer_mode:
        developer_mode["file_debug"] = default_developer_mode["file_debug"]

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


dev_mode = _setup()
