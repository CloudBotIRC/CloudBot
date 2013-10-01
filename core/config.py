import json
import os
import time
import sys

from watchdog.observers import Observer
from watchdog.tricks import Trick


class Config(dict):
    def __init__(self, name, logger, *args, **kwargs):
        self.filename = "{}.config.json".format(name)
        self.path = os.path.abspath(self.filename)
        self.logger = logger
        self.update(*args, **kwargs)

        # load self
        self.load_config()

        # start reloader
        self.watcher()

    def load_config(self):
        if not os.path.exists(self.path):
            # if there is no config, show an error and die
            self.logger.critical("No config file found, bot shutting down!")
            print "No config file found! Bot shutting down in five seconds."
            print "Copy 'cloudbot.default.json' to 'cloudbot.config.json' for defaults."
            print "For help, see http://git.io/cloudbotirc. Thank you for using CloudBot!"
            time.sleep(5)
            sys.exit()

        with open(self.path) as f:
            self.update(json.load(f))
            self.logger.info("Config loaded from file.")

    def save_config(self):
        json.dump(self, open(self.path, 'w'), sort_keys=True, indent=2)
        self.logger.info("Config saved to file.")


    def watcher(self):
        pattern = "*{}".format(self.filename)
        event_handler = ConfigReloader(self, patterns=[pattern])
        self.observer = Observer()
        self.observer.schedule(event_handler,
                               path='.',
                               recursive=True
                               )
        self.observer.start()

 
class ConfigReloader(Trick):
    def __init__(self, config, *args, **kwargs):
        self.config = config
        self.logger = config.logger
        Trick.__init__(self, *args, **kwargs)

    def on_any_event(self, event):
        self.logger.info("Config changed, triggering reload.")
        self.config.load_config()
