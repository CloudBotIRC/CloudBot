import time
import logging
import re
import os

from core import config, irc


def clean_name(n):
    """strip all spaces and capitalization"""
    return re.sub('[^A-Za-z0-9_]+', '', n.replace(" ", "_"))


class Bot(object):
    def __init__(self, name):
        # basic variables
        self.name = name
        self.start_time = time.time()

        # set up config and logging
        self.setup()
        self.logger.debug("Bot setup completed.")

        # start IRC connections
        self.connections = {}
        self.connect()

    def connect(self):
        """connect to all the networks defined in the bot config"""
        for conf in self.config['connections']:
            # strip all spaces and capitalization from the connection name
            name = clean_name(conf['name'])
            nick = conf['nick']
            server = conf['connection']['server']
            port = conf['connection'].get('port', 6667)

            self.logger.debug("({}) Creating connection to {}.".format(name, server))

            if conf['connection'].get('ssl'):
                self.connections[name] = irc.SSLIRC(name, server, nick, conf = conf,
                                     port = port, channels = conf['channels'],
                                     ignore_certificate_errors=conf['connection'].get('ignore_cert', True))
                self.logger.debug("({}) Created SSL connection.".format(name))   
            else:
                self.connections[name] = irc.IRC(name, server, nick, conf = conf,
                                                 port = port, channels = conf['channels'])
                self.logger.debug("({}) Created connection.".format(name))  

    def setup(self):
        """create the logger and config objects"""
        # logging
        self.logger = self.get_logger()
        self.logger.debug("Logging engine started.")

        # data folder
        self.data_dir = os.path.abspath('data')
        if not os.path.exists(self.data_dir):
            self.logger.debug("Data folder not found, creating.")
            os.mkdir(self.data_dir)
            self.logger.debug("Created data folder.")

        # config
        self.config = self.get_config()
        self.logger.debug("Config object created.")


    def get_config(self):
        """create and return the config object"""
        return config.Config(self.name, self.logger)


    def get_logger(self):
        """create and return the logger object"""
        # create logger
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)

        # add a file handler
        log_name = "{}.log".format(self.name)
        fh = logging.FileHandler(log_name)
        fh.setLevel(logging.DEBUG)

        # stdout handler
        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)

        # create a formatter and set the formatter for the handler.
        frmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        fh.setFormatter(frmt)
        simple_frmt = logging.Formatter('[%(levelname)s] %(message)s')
        sh.setFormatter(simple_frmt)

        # add the Handlers to the logger
        logger.addHandler(fh)
        logger.addHandler(sh)
        return logger
