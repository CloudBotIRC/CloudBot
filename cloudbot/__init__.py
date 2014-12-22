import sys

# check python version
if sys.version_info < (3, 4, 0):
    print("CloudBot requires Python 3.4 or newer.")
    sys.exit(1)

import json
import logging.config
import logging
import os

__version__ = "1.0.0.dev0"


def _setup():
    default_developer_mode = {"console_debug": False, "file_debug": True}
    if os.path.exists(os.path.abspath("config.json")):
        with open(os.path.abspath("config.json")) as config_file:
            json_conf = json.load(config_file)
        developer_mode = json_conf.get("developer_mode", default_developer_mode)
    else:
        developer_mode = default_developer_mode

    if not "console_debug" in developer_mode:
        developer_mode["console_debug"] = default_developer_mode["console_debug"]
    if not "file_debug" in developer_mode:
        developer_mode["file_debug"] = default_developer_mode["file_debug"]

    logging_dir = os.path.join(os.path.abspath(os.path.curdir), "logs")

    if not os.path.exists(logging_dir):
        os.makedirs(logging_dir)

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
                "filename": os.path.join(logging_dir, "bot.log")
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
            "filename": os.path.join(logging_dir, "debug.log")
        }
        dict_config["loggers"]["cloudbot"]["handlers"].append("debug_file")

    logging.config.dictConfig(dict_config)

    return logging_dir, developer_mode


log_dir, dev_mode = _setup()
