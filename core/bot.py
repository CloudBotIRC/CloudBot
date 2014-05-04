import time
import logging
import re
import os
import sys
import queue

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.schema import MetaData

from util import botvars
from core import config, irc, main
from core.loader import PluginLoader
from core.pluginmanager import PluginManager

logger_initialized = False


def clean_name(n):
    """strip all spaces and capitalization
    :type n: str
    :rtype: str
    """
    return re.sub('[^A-Za-z0-9_]+', '', n.replace(" ", "_"))


def get_logger():
    """create and return a new logger object
    :rtype: logging.Logger
    """
    # create logger
    logger = logging.getLogger("cloudbot")
    global logger_initialized
    if logger_initialized:
        # Only initialize once
        return logger

    logger.setLevel(logging.DEBUG)

    # add a file handler
    file_handler = logging.FileHandler("bot.log")
    file_handler.setLevel(logging.INFO)

    # add debug file handler
    debug_file_handler = logging.FileHandler("debug.log")
    debug_file_handler.setLevel(logging.DEBUG)

    # stdout handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # create a formatter and set the formatter for the handler.
    file_formatter = logging.Formatter('%(asctime)s[%(levelname)s] %(message)s', '[%Y-%m-%d][%H:%M:%S]')
    console_formatter = logging.Formatter('%(asctime)s[%(levelname)s] %(message)s', '[%H:%M:%S]')
    file_handler.setFormatter(file_formatter)
    debug_file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    # add the Handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(debug_file_handler)
    logger.addHandler(console_handler)

    # be sure to set initialized = True
    logger_initialized = True
    return logger


class CloudBot:
    """
    :type start_time: float
    :type running: bool
    :type do_restart: bool
    :type connections: list[core.irc.BotConnection]
    :type logger: logging.Logger
    :type data_dir: bytes
    :type config: core.config.Config
    :type plugin_manager: core.pluginmanager.PluginManager
    :type loader: core.loader.PluginLoader
    """

    def __init__(self):
        # basic variables
        self.start_time = time.time()
        self.running = True
        self.do_restart = False

        # stores all queued messages from all connections
        self.queued_messages = queue.Queue()
        # format: [{
        #   "conn": BotConnection, "raw": str, "prefix": str, "command": str, "params": str, "nick": str,
        #   "user": str, "host": str, "mask": str, "paramlist": list[str], "lastparam": str
        # }]

        # stores each bot server connection
        self.connections = []

        # set up logging
        self.logger = get_logger()
        self.logger.debug("Logging system initialised.")

        # declare and create data folder
        self.data_dir = os.path.abspath('data')
        if not os.path.exists(self.data_dir):
            self.logger.debug("Data folder not found, creating.")
            os.mkdir(self.data_dir)

        # set up config
        self.config = config.Config(self)
        self.logger.debug("Config system initialised.")

        # setup db
        db_path = self.config.get('database', 'sqlite:///cloudbot.db')
        self.db_engine = create_engine(db_path)
        self.db_factory = sessionmaker(bind=self.db_engine)
        self.db_session = scoped_session(self.db_factory)
        self.db_metadata = MetaData()
        # set botvars.metadata so plugins can access when loading
        botvars.metadata = self.db_metadata
        self.logger.debug("Database system initialised.")

        # Bot initialisation complete
        self.logger.debug("Bot setup completed.")

        self.threads = {}

        # create bot connections
        self.create_connections()

        # run plugin loader
        self.plugin_manager = PluginManager(self)

        self.loader = PluginLoader(self)

    def start(self):
        """
        Starts CloudBot.
        This method first connects all of the IRC connections, then receives input from the IRC engine and processes it
        """
        # start connections
        for conn in self.connections:
            conn.connect()

        self.logger.info("Starting main thread.")
        while self.running:
            # This method will block until a new message is received.
            message = self.queued_messages.get()

            if not self.running:
                # When the bot is stopped, StopIteration is put into the queue to make sure that
                # self.queued_messages.get() doesn't block this thread forever.
                # But we don't actually want to process that message, so if we're stopped, just exit.
                return

            if message.get("reconnect", False):
                # The IRC engine will put {"reconnect": True, "conn": BotConnection} into the message queue when the
                # connection times out, and it needs to be restarted. We'll do that.
                connection = message["conn"]
                self.logger.info("[{}] Reconnecting to IRC server".format(connection.readable_name))
                connection.connection.reconnect()
                # We've dealt with this message, no need to send it to main
                continue

            main.main(self, message)

    def create_connections(self):
        """ Create a BotConnection for all the networks defined in the config """
        for conf in self.config['connections']:
            # strip all spaces and capitalization from the connection name
            readable_name = conf['name']
            name = clean_name(readable_name)
            nick = conf['nick']
            server = conf['connection']['server']
            port = conf['connection'].get('port', 6667)

            self.logger.debug("Creating BotInstance for {}.".format(name))

            self.connections.append(irc.BotConnection(self, name, server, nick, config=conf,
                                                      port=port, logger=self.logger, channels=conf['channels'],
                                                      ssl=conf['connection'].get('ssl', False),
                                                      readable_name=readable_name))
            self.logger.debug("[{}] Created connection.".format(readable_name))

    def stop(self, reason=None):
        """quits all networks and shuts the bot down"""
        self.logger.info("Stopping bot.")

        self.logger.debug("Stopping config reloader.")
        self.config.stop()

        self.logger.debug("Stopping plugin loader.")
        self.loader.stop()

        for connection in self.connections:
            self.logger.debug("[{}] Closing connection.".format(connection.readable_name))

            if reason:
                connection.cmd("QUIT", [reason])
            else:
                connection.cmd("QUIT")

            connection.stop()

        if not self.do_restart:
            # Don't shut down logging if restarting
            self.logger.debug("Stopping logging engine")
            logging.shutdown()
        self.running = False
        # We need to make sure that the main loop actually exists after this method is called. This will ensure that the
        # blocking queued_messages.get() method is executed, then the method will stop without processing it because
        # self.running = False
        self.queued_messages.put(StopIteration)

    def restart(self, reason=None):
        """shuts the bot down and restarts it"""
        self.do_restart = True
        self.stop(reason)
