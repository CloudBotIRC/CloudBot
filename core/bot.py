import time
import logging
import re
import os
import Queue
import collections
import threading

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine

from core import config, irc, main
from core.permissions import PermissionManager
from core.loader import PluginLoader


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
    fh.setLevel(logging.INFO)

    # stdout handler
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)

    # create a formatter and set the formatter for the handler.
    frmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    fh.setFormatter(frmt)
    simple_frmt = logging.Formatter('[%(levelname)s] %(message)s')
    sh.setFormatter(simple_frmt)

    # add the Handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


class Bot(threading.Thread):
    def __init__(self):
        # basic variables
        self.start_time = time.time()
        self.running = True
        self.do_restart = False
        self.connections = []

        # set up config and logging
        self.setup()
        self.logger.debug("Bot setup completed.")

        # start IRC connections
        self.connect()
        print self.connections

        for conn in self.connections:
            conn.permissions = PermissionManager(self, conn)
            print conn

        # run plugin loader
        self.plugins = collections.defaultdict(list)
        self.threads = {}

        self.loader = PluginLoader(self)

        threading.Thread.__init__(self)


    def run(self):
        """recieves input from the IRC engine and processes it"""
        self.logger.info("Starting main thread.")
        while self.running:
            for conn in self.connections:
                try:
                    incoming = conn.parsed_queue.get_nowait()
                    if incoming == StopIteration:
                        print "StopIteration"
                        # IRC engine has signalled timeout, so reconnect (ugly)
                        conn.connection.reconnect()
                    main.main(self, conn, incoming)
                except Queue.Empty:
                    pass

            # if no messages are in the incoming queue, sleep
            while self.running and all(c.parsed_queue.empty() for c in self.connections):
                time.sleep(.1)


    def setup(self):
        """create the logger and config objects"""
        # logging
        self.logger = get_logger()
        self.logger.debug("Logging system initalised.")

        # data folder
        self.data_dir = os.path.abspath('persist')
        if not os.path.exists(self.data_dir):
            self.logger.debug("Data folder not found, creating.")
            os.mkdir(self.data_dir)

        # config
        self.config = config.Config(self)
        self.logger.debug("Config system initalised.")

        # db
        engine = create_engine('sqlite:///cloudbot.db')
        db_factory = sessionmaker(bind=engine)
        self.db_session = scoped_session(db_factory)
        self.logger.debug("Database system initalised.")


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
                self.connections.append(irc.SSLIRC(name, server, nick, config = conf,
                                     port = port, channels = conf['channels'],
                                     ignore_certificate_errors=conf['connection'].get('ignore_cert', True)))
                self.logger.debug("({}) Created SSL connection.".format(name))   
            else:
                self.connections.append(irc.IRC(name, server, nick, config = conf,
                                                 port = port, channels = conf['channels']))
                self.logger.debug("({}) Created connection.".format(name)) 


    def stop(self, reason=None):
        """quits all networks and shuts the bot down"""
        self.logger.info("Stopping bot.")

        self.config.observer.stop()
        self.logger.debug("Stopping config reloader.")

        self.loader.stop()
        self.logger.debug("Stopping plugin loader.")

        for connection in self.connections:
            self.logger.debug("({}) Closing connection.".format(connection.name))

            if reason:
                connection.cmd("QUIT", [reason])
            else:
                connection.cmd("QUIT")

            connection.stop()

        self.logger.debug("Logging engine stopped")
        logging.shutdown()

        self.running = False


    def restart(self, reason=None):
        """shuts the bot down and restarts it"""
        self.do_restart = True
        self.stop(reason)
