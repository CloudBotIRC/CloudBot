import time
import logging

import config

class Bot(object):
    def __init__(self, name):
        # basic variables
        self.name = name
        self.start_time = time.time()

        # set up config and logging
        self.setup()
        print self.config


    def setup(self):
        # logging
        self.logger = self.get_logger()
        self.logger.debug("Logging engine started.")

        # logging
        self.config = self.get_config()
        self.config.reload()
        self.logger.debug("Config loaded.")

    def get_config(self):
        return config.Config(self.name)

    def get_logger(self):
        # create logger
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)

        # add a file handler
        log_name = "{}.log".format(self.name)
        fh = logging.FileHandler(log_name)
        fh.setLevel(logging.DEBUG)

        # create a formatter and set the formatter for the handler.
        frmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        fh.setFormatter(frmt)

        # add the Handler to the logger
        logger.addHandler(fh)
        return logger
