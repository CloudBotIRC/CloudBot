import asyncio
import time
import logging
import re
import os
import gc

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.schema import MetaData

import cloudbot
from cloudbot.core.connection import BotConnection
from cloudbot.core.config import Config
from cloudbot.core.reloader import PluginReloader
from cloudbot.core.pluginmanager import PluginManager
from cloudbot.core.events import BaseEvent, CommandEvent, RegexEvent
from cloudbot.util import botvars, formatting

logger_initialized = False


def clean_name(n):
    """strip all spaces and capitalization
    :type n: str
    :rtype: str
    """
    return re.sub('[^A-Za-z0-9_]+', '', n.replace(" ", "_"))


class CloudBot:
    """
    :type start_time: float
    :type running: bool
    :type do_restart: bool
    :type connections: list[cloudbot.core.connection.BotConnection]
    :type logger: logging.Logger
    :type data_dir: bytes
    :type config: core.config.Config
    :type plugin_manager: cloudbot.core.pluginmanager.PluginManager
    :type reloader: cloudbot.core.reloader.PluginReloader
    :type db_engine: sqlalchemy.engine.Engine
    :type db_factory: sqlalchemy.orm.session.sessionmaker
    :type db_session: sqlalchemy.orm.scoping.scoped_session
    :type db_metadata: sqlalchemy.sql.schema.MetaData
    """

    def __init__(self, loop=asyncio.get_event_loop()):
        # basic variables
        self.loop = loop
        self.start_time = time.time()
        self.running = True
        self.do_restart = False

        # stores all queued messages from all connections
        self.queued_events = asyncio.Queue(loop=self.loop)

        # stores each bot server connection
        self.connections = []

        # set up logging
        self.logger = logging.getLogger("cloudbot")
        self.logger.debug("Logging system initialised.")

        # declare and create data folder
        self.data_dir = os.path.abspath('data')
        if not os.path.exists(self.data_dir):
            self.logger.debug("Data folder not found, creating.")
            os.mkdir(self.data_dir)

        # set up config
        self.config = Config(self)
        self.logger.debug("Config system initialised.")

        # log developer mode
        if cloudbot.dev_mode.get("plugin_reloading"):
            self.logger.info("Enabling developer option: plugin reloading.")
        if cloudbot.dev_mode.get("config_reloading"):
            self.logger.info("Enabling developer option: config reloading.")
        if cloudbot.dev_mode.get("console_debug"):
            self.logger.info("Enabling developer option: console debug.")
        if cloudbot.dev_mode.get("file_debug"):
            self.logger.info("Enabling developer option: file debug")

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

        # create bot connections
        self.create_connections()

        if cloudbot.dev_mode.get("plugin_reloading"):
            self.reloader = PluginReloader(self)

        self.plugin_manager = PluginManager(self)

    def run(self):
        """
        Starts CloudBot.
        This will first load plugins, then connect to IRC, then start the main loop for processing input.
        """
        self.loop.run_until_complete(self.main_loop())
        self.loop.close()

    def create_connections(self):
        """ Create a BotConnection for all the networks defined in the config """
        for conf in self.config['connections']:
            # strip all spaces and capitalization from the connection name
            readable_name = conf['name']
            name = clean_name(readable_name)
            nick = conf['nick']
            server = conf['connection']['server']
            port = conf['connection'].get('port', 6667)

            self.connections.append(BotConnection(self, name, server, nick, config=conf,
                                                  port=port, logger=self.logger, channels=conf['channels'],
                                                  use_ssl=conf['connection'].get('ssl', False),
                                                  readable_name=readable_name))
            self.logger.debug("[{}] Created connection.".format(readable_name))

    def stop(self, reason=None):
        """quits all networks and shuts the bot down"""
        self.logger.info("Stopping bot.")

        if cloudbot.dev_mode.get("config_reloading"):
            self.logger.debug("Stopping config reloader.")
            self.config.stop()

        if cloudbot.dev_mode.get("plugin_reloading"):
            self.logger.debug("Stopping plugin reloader.")
            self.reloader.stop()

        for connection in self.connections:
            if not connection.connected:
                # Don't close a connection that hasn't connected
                continue
            self.logger.debug("[{}] Closing connection.".format(connection.readable_name))

            if reason:
                connection.cmd("QUIT", [reason])
            else:
                connection.cmd("QUIT")

            connection.stop()

        self.running = False
        # We need to make sure that the main loop actually exists after this method is called. This will ensure that the
        # blocking queued_events.get() method is executed, then the method will stop without processing it because
        # self.running = False
        self.queued_events.put_nowait(StopIteration)

    def restart(self, reason=None):
        """shuts the bot down and restarts it"""
        self.do_restart = True
        self.stop(reason)

    @asyncio.coroutine
    def main_loop(self):
        # load plugins
        yield from self.plugin_manager.load_all(os.path.abspath("plugins"))
        # if we we're stopped while loading plugins, cancel that and just stop
        if not self.running:
            return

        if cloudbot.dev_mode.get("plugin_reloading"):
            # start plugin reloader
            self.reloader.start(os.path.abspath("plugins"))

        # start connections
        yield from asyncio.gather(*[conn.connect() for conn in self.connections], loop=self.loop)
        # run a manual garbage collection cycle, to clean up any unused objects created during initialization
        gc.collect()
        # start main loop
        self.logger.info("Starting main loop")
        while self.running:
            # This function will wait until a new message is received.
            event = yield from self.queued_events.get()

            if not self.running:
                # When the bot is stopped, StopIteration is put into the queue to make sure that
                # self.queued_events.get() doesn't block this thread forever.
                # But we don't actually want to process that message, so if we're stopped, just exit.
                return

            # process the message
            asyncio.async(self.process(event), loop=self.loop)

    @asyncio.coroutine
    def process(self, event):
        """
        :type self: cloudbot.core.bot.CloudBot
        :type event: cloudbot.core.events.BaseEvent
        """
        command_prefix = event.conn.config.get('command_prefix', '.')

        # EVENTS
        if event.irc_command in self.plugin_manager.raw_triggers:
            for raw_hook in self.plugin_manager.raw_triggers[event.irc_command]:
                yield from self.plugin_manager.launch(raw_hook, BaseEvent(bot=self, base_event=event))
        for raw_hook in self.plugin_manager.catch_all_events:
            yield from self.plugin_manager.launch(raw_hook, BaseEvent(bot=self, base_event=event))

        if event.irc_command == 'PRIVMSG':
            # COMMANDS
            if event.chan == event.nick:  # private message, no command prefix
                prefix = '^(?:[{}]?|'.format(command_prefix)
            else:
                prefix = '^(?:[{}]|'.format(command_prefix)
            command_re = prefix + event.conn.nick
            command_re += r'[,;:]+\s+)(\w+)(?:$|\s+)(.*)'

            match = re.match(command_re, event.irc_message)

            if match:
                command = match.group(1).lower()
                if command in self.plugin_manager.commands:
                    command_hook = self.plugin_manager.commands[command]
                    command_event = CommandEvent(bot=self, text=match.group(2).strip(),
                                                 triggered_command=command, base_event=event)
                    yield from self.plugin_manager.launch(command_hook, command_event)
                else:
                    potential_matches = []
                    for potential_match, plugin in self.plugin_manager.commands.items():
                        if potential_match.startswith(command):
                            potential_matches.append((potential_match, plugin))
                    if potential_matches:
                        if len(potential_matches) == 1:
                            command_event = CommandEvent(bot=self, text=match.group(2).strip(),
                                                         triggered_command=command, base_event=event)
                            yield from self.plugin_manager.launch(potential_matches[0][1], command_event)
                        else:
                            event.notice("Possible matches: {}".format(
                                formatting.get_text_list([command for command, plugin in potential_matches])))

            # REGEXES
            for regex, regex_hook in self.plugin_manager.regex_hooks:
                match = regex.search(event.irc_message)
                if match:
                    regex_event = RegexEvent(bot=self, match=match, base_event=event)
                    yield from self.plugin_manager.launch(regex_hook, regex_event)
