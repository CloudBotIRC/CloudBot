import time
import logging
import re
import os
import threading
import sys

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine

import queue
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


class CloudBot(threading.Thread):
    """
    :type start_time: float
    :type running: bool
    :type do_restart: bool
    :type connections: list[core.irc.BotConnection]
    :type commands: list
    :type logger: logging.Logger
    :type data_dir: bytes
    :type config: core.config.Config
    :type db_session: scoped_session
    :type modules: dict
    :type loader: core.loader.PluginLoader
    """

    def __init__(self):
        # basic variables
        self.start_time = time.time()
        self.running = True
        self.do_restart = False

        # stores each bot server connection
        self.connections = []

        # set up logging
        self.logger = get_logger()
        self.logger.debug("Logging system initalised.")

        # declare and create data folder
        self.data_dir = os.path.abspath('data')
        if not os.path.exists(self.data_dir):
            self.logger.debug("Data folder not found, creating.")
            os.mkdir(self.data_dir)

        # set up config
        self.config = config.Config(self)
        self.logger.debug("Config system initalised.")

        # setup db
        engine = create_engine('sqlite:///cloudbot.db')
        db_factory = sessionmaker(bind=engine)
        self.db_session = scoped_session(db_factory)
        self.logger.debug("Database system initalised.")

        # Bot initialisation complete
        self.logger.debug("Bot setup completed.")

        # run plugin loader
        self.plugin_manager = PluginManager(self)

        """ self.modules format
        {'PLUGIN_TYPE': [(<COMPILED_PLUGIN_FUNTION>,
                          {PLUGIN_ARGS}),
                         (<COMPILED_PLUGIN_FUNTION>,
                          {PLUGIN_ARGS})],
        'PLUGIN_TYPE': [(<COMPILED_PLUGIN_FUNTION>,
                          {PLUGIN_ARGS})]
        }
        """

        self.threads = {}

        self.loader = PluginLoader(self)

        # start bot connections
        self.create_connections()

        threading.Thread.__init__(self)

    def run(self):
        """recieves input from the IRC engine and processes it"""
        self.logger.info("Starting main thread.")
        while self.running:
            for connection in self.connections:
                try:
                    incoming = connection.parsed_queue.get_nowait()
                    if incoming == StopIteration:
                        print("StopIteration")
                        # IRC engine has signalled timeout, so reconnect (ugly)
                        connection.connection.reconnect()
                    main.main(self, connection, incoming)
                except queue.Empty:
                    pass

            # if no messages are in the incoming queue, sleep
            while self.running and all(connection.parsed_queue.empty() for connection in self.connections):
                time.sleep(.1)

    def create_connections(self):
        """ Create a BotConnection for all the networks defined in the config """
        for conf in self.config['connections']:
            # strip all spaces and capitalization from the connection name
            name = clean_name(conf['name'])
            nick = conf['nick']
            server = conf['connection']['server']
            port = conf['connection'].get('port', 6667)

            self.logger.debug("Creating BotInstance for {}.".format(name))

            self.connections.append(irc.BotConnection(self, name, server, nick, config=conf,
                                                      port=port, logger=self.logger, channels=conf['channels'],
                                                      ssl=conf['connection'].get('ssl', False)))
            self.logger.debug("({}) Created connection.".format(name))

    def stop(self, reason=None):
        """quits all networks and shuts the bot down"""
        self.logger.info("Stopping bot.")

        self.config.stop()
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

        if not self.do_restart:
            # Don't shut down logging if restarting
            self.logger.debug("Stopping logging engine")
            logging.shutdown()
        self.running = False

    def restart(self, reason=None):
        """shuts the bot down and restarts it"""
        self.do_restart = True
        self.stop(reason)
