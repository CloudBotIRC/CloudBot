import json
import os
import time
import sys


class Config(dict):
    def __init__(self, name, logger, *args, **kwargs):
        self.path = os.path.abspath("{}.config.json".format(name))
        self.logger = logger
        self.update(*args, **kwargs)

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
            self.logger.info("Config reloaded.")

    def save_config(self):
        json.dump(self, open(self.path, 'w'), sort_keys=True, indent=2)
