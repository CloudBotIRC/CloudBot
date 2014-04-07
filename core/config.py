import json
import os
import time
import sys

from watchdog.observers import Observer
from watchdog.tricks import Trick


class Config(dict):
    def __init__(self, bot, *args, **kwargs):
        """
        :type bot: core.bot.CloudBot
        """
        self.filename = "config.json"
        self.path = os.path.abspath(self.filename)
        self.bot = bot
        self.logger = bot.logger
        self.update(*args, **kwargs)

        # populate self with config data
        self.load_config()

        # Declaring here, to be assigned later
        self.observer = None
        self.event_handler = None
        # start watcher
        self.watcher()

    def load_config(self):
        """(re)loads the bot config from the config file"""
        if not os.path.exists(self.path):
            # if there is no config, show an error and die
            self.logger.critical("No config file found, bot shutting down!")
            print("No config file found! Bot shutting down in five seconds.")
            print("Copy 'config.default' to 'config.json' for defaults.")
            print("For help, see http://git.io/cloudbotirc. Thank you for using CloudBot!")
            time.sleep(5)
            sys.exit()

        with open(self.path) as f:
            self.update(json.load(f))
            self.logger.info("Config loaded from file.")

        # reload permissions
        if self.bot.connections:
            for connection in self.bot.connections:
                connection.permissions.reload()

    def save_config(self):
        """saves the contents of the config dict to the config file"""
        json.dump(self, open(self.path, 'w'), sort_keys=True, indent=2)
        self.logger.info("Config saved to file.")

    def watcher(self):
        """starts the watchdog to automatically reload the config when it changes on disk"""
        self.observer = Observer()

        pattern = "*{}".format(self.filename)

        self.event_handler = ConfigEventHandler(self.bot, self, patterns=[pattern])
        self.observer.schedule(self.event_handler, path='.', recursive=False)
        self.observer.start()


class ConfigEventHandler(Trick):
    def __init__(self, bot, config, *args, **kwargs):
        """
        :type bot: core.bot.CloudBot
        :type config: Config
        """
        self.bot = bot
        self.config = config
        self.logger = config.logger
        Trick.__init__(self, *args, **kwargs)

    def on_any_event(self, event):
        if self.bot.running:
            self.logger.info("Config changed, triggering reload.")
            self.config.load_config()
