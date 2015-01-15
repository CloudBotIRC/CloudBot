import json
import os
import time
import sys
import logging

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

logger = logging.getLogger("cloudbot")


class Config(dict):
    """
    :type filename: str
    :type path: str
    :type bot: cloudbot.bot.CloudBot
    :type observer: Observer
    :type event_handler: ConfigEventHandler
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
        self.reloading_enabled = self.get("reloading", {}).get("config_reloading", True)

        if self.reloading_enabled:
            # start watcher
            self.observer = Observer()

            pattern = "*{}".format(self.filename)

            self.event_handler = ConfigEventHandler(self.bot, self, patterns=[pattern])
            self.observer.schedule(self.event_handler, path='.', recursive=False)
            self.observer.start()

    def stop(self):
        """shuts down the config reloader"""
        if self.reloading_enabled:
            self.observer.stop()

    def load_config(self):
        """(re)loads the bot config from the config file"""
        if not os.path.exists(self.path):
            # if there is no config, show an error and die
            logger.critical("No config file found, bot shutting down!")
            print("No config file found! Bot shutting down in five seconds.")
            print("Copy 'config.default.json' to 'config.json' for defaults.")
            print("For help, see http://git.io/cloudbotirc. Thank you for using CloudBot!")
            time.sleep(5)
            sys.exit()

        with open(self.path) as f:
            self.update(json.load(f))
            logger.debug("Config loaded from file.")

        # reload permissions
        if self.bot.connections:
            for connection in self.bot.connections.values():
                connection.permissions.reload()

    def save_config(self):
        """saves the contents of the config dict to the config file"""
        json.dump(self, open(self.path, 'w'), sort_keys=True, indent=4)
        logger.info("Config saved to file.")


class ConfigEventHandler(PatternMatchingEventHandler):
    """
    :type bot: cloudbot.bot.CloudBot
    :type config: core.config.Config
    :type logger: logging.Logger
    """

    def __init__(self, bot, config, *args, **kwargs):
        """
        :type bot: cloudbot.bot.CloudBot
        :type config: Config
        """
        self.bot = bot
        self.config = config
        PatternMatchingEventHandler.__init__(self, *args, **kwargs)

    def on_any_event(self, event):
        if self.bot.running:
            logger.info("Config changed, triggering reload.")
            self.config.load_config()
