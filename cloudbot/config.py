import json
import os
import time
import sys
import logging

from watchdog.observers import Observer

logger = logging.getLogger("cloudbot")


class Config(dict):
    """
    :type filename: str
    :type path: str
    :type bot: cloudbot.bot.CloudBot
    """

    def __init__(self, bot, *args, **kwargs):
        """
        :type bot: cloudbot.bot.CloudBot
        :type args: list
        :type kwargs: dict
        """
        super().__init__(*args, **kwargs)
        self.filename = "config.json"
        self.path = os.path.abspath(self.filename)
        self.bot = bot
        self.update(*args, **kwargs)

        # populate self with config data
        self.load_config()

    def load_config(self):
        """(re)loads the bot config from the config file"""
        if not os.path.exists(self.path):
            # if there is no config, show an error and die
            logger.critical("No config file found, bot shutting down!")
            print("No config file found, please copy 'config.default.json' to 'config.json' and customize!")
            print("Stopping in 5 seconds.")
            time.sleep(5)
            sys.exit()

        with open(self.path) as f:
            self.update(json.load(f))
            logger.debug("Config loaded from file.")

        # reload permissions
        if self.bot.connections:
            for connection in self.bot.connections:
                connection.permissions.reload()

    def save_config(self):
        """saves the contents of the config dict to the config file"""
        json.dump(self, open(self.path, 'w'), sort_keys=True, indent=4)
        logger.info("Config saved to file.")
