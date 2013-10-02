import time
import logging
import sys
import re
import os
import Queue
import collections

from core import config, irc, main, loader


def clean_name(n):
    """strip all spaces and capitalization"""
    return re.sub('[^A-Za-z0-9_]+', '', n.replace(" ", "_"))

def get_logger():
    """create and return a new logger object"""
    # create logger
    logger = logging.getLogger("cloudbot")
    logger.setLevel(logging.DEBUG)

    # add a file handler
    log_name = "bot.log"
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


class Bot(object):

    def __init__(self):
        # basic variables
        self.start_time = time.time()
        self.running = True

        # set up config and logging
        self.setup()
        self.logger.debug("Bot setup completed.")

        # start IRC connections
        self.connections = {}
        self.connect()

        # run plugin loader
        self.plugins = collections.defaultdict(list)
        self.threads = {}
        self.loader = loader.PluginLoader(self)


    def loop(self):
        """recieves input from the IRC engine and processes it"""

        for conn in self.connections.itervalues():
            try:
                incoming = conn.parsed_queue.get_nowait()
                main.main(self, conn, incoming)
            except Queue.Empty:
                pass

        # if no messages are in the incoming queue, sleep
        while all(connection.parsed_queue.empty() for connection in self.connections.itervalues()):
            time.sleep(.1)


    def setup(self):
        """create the logger and config objects"""
        # logging
        self.logger = get_logger()
        self.logger.debug("Logging engine started.")

        # data folder
        self.data_dir = os.path.abspath('data')
        if not os.path.exists(self.data_dir):
            self.logger.debug("Data folder not found, creating.")
            os.mkdir(self.data_dir)
            self.logger.debug("Created data folder.")

        # config
        self.config = config.Config(self.logger)
        self.logger.debug("Config object created.")


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


    def stop(self, reason=None):
        """quits all networks and shuts the bot down"""
        self.logger.info("Stopping bot.")
        self.running = False

        # wait for the bot loop to stop
        time.sleep(1)
        self.config.observer.stop()
        self.logger.debug("Stopping config reloader.")

        self.loader.stop()
        self.logger.debug("Stopping plugin loader.")

        for name, connection in self.connections.iteritems():
            self.logger.debug("({}) Closing connection.".format(name))

            if reason:
                connection.cmd("QUIT", [reason])
            else:
                connection.cmd("QUIT")

            connection.stop()

        self.logger.debug("Logging engine stopped")
        logging.shutdown()
        sys.exit()

