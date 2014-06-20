import sys

# check python version
if sys.version_info < (3, 4, 0):
    print("CloudBot3 requires Python 3.4 or newer.")
    sys.exit(1)

import json
import logging.config
import logging
import os

__version__ = "0.1.1.dev0"

__all__ = ["util", "bot", "connection", "config", "permissions", "plugin", "event", "hook", "dev_mode", "log_dir"]


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

    global log_dir
    log_dir = os.path.join(os.path.abspath(os.path.curdir), "logs")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

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
                "filename": os.path.join(log_dir, "bot.log")
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
            "filename": os.path.join(log_dir, "debug.log")
        }
        dict_config["loggers"]["cloudbot"]["handlers"].append("debug_file")

    logging.config.dictConfig(dict_config)

    return developer_mode


dev_mode = _setup()
