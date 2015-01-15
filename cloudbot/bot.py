import asyncio
import time
import logging
import re
import os
import gc

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.schema import MetaData

from cloudbot.client import Client
from cloudbot.config import Config
from cloudbot.plugin import PluginManager
from cloudbot.event import Event, CommandEvent, RegexEvent, EventType
from cloudbot.util import botvars, formatting
from cloudbot.clients.irc import IrcClient

logger = logging.getLogger("cloudbot")


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
    :type connections: list[Client | IrcClient]
    :type data_dir: bytes
    :type config: core.config.Config
    :type plugin_manager: PluginManager
    :type db_engine: sqlalchemy.engine.Engine
    :type db_factory: sqlalchemy.orm.session.sessionmaker
    :type db_session: sqlalchemy.orm.scoping.scoped_session
    :type db_metadata: sqlalchemy.sql.schema.MetaData
    :type loop: asyncio.events.AbstractEventLoop
    :type stopped_future: asyncio.Future
    :param: stopped_future: Future that will be given a result when the bot has stopped.
    """

    def __init__(self, loop=asyncio.get_event_loop()):
        # basic variables
        self.loop = loop
        self.start_time = time.time()
        self.running = True
        # future which will be called when the bot stops
        self.stopped_future = asyncio.Future(loop=self.loop)

        # stores each bot server connection
        self.connections = []

        # for plugins
        self.logger = logger

        # declare and create data folder
        self.data_dir = os.path.abspath('data')
        if not os.path.exists(self.data_dir):
            logger.debug("Data folder not found, creating.")
            os.mkdir(self.data_dir)

        # set up config
        self.config = Config(self)
        logger.debug("Config system initialised.")

        # set values for reloading
        self.plugin_reloading_enabled = self.config.get("reloading", {}).get("plugin_reloading", False)
        self.config_reloading_enabled = self.config.get("reloading", {}).get("config_reloading", True)

        # this doesn't REALLY need to be here but it's nice
        self.user_agent = self.config.get('user_agent', 'CloudBot/3.0 - CloudBot Refresh '
                                                        '<https://github.com/CloudBotIRC/CloudBot/>')

        # setup db
        db_path = self.config.get('database', 'sqlite:///cloudbot.db')
        self.db_engine = create_engine(db_path)
        self.db_factory = sessionmaker(bind=self.db_engine)
        self.db_session = scoped_session(self.db_factory)
        self.db_metadata = MetaData()

        # set botvars.metadata so plugins can access when loading
        botvars.metadata = self.db_metadata
        logger.debug("Database system initialised.")

        # Bot initialisation complete
        logger.debug("Bot setup completed.")

        # create bot connections
        self.create_connections()

        self.plugin_manager = PluginManager(self)

    def run(self):
        """
        Starts CloudBot.
        This will load plugins, connect to IRC, and process input.
        :return: True if CloudBot should be restarted, False otherwise
        :rtype: bool
        """
        # Initializes the bot, plugins and connections
        self.loop.run_until_complete(self._init_routine())
        # Wait till the bot stops. The stopped_future will be set to True to restart, False otherwise
        restart = self.loop.run_until_complete(self.stopped_future)
        self.loop.close()
        return restart

    def create_connections(self):
        """ Create a BotConnection for all the networks defined in the config """
        for config in self.config['connections']:
            # strip all spaces and capitalization from the connection name
            name = clean_name(config['name'])
            nick = config['nick']
            server = config['connection']['server']
            port = config['connection'].get('port', 6667)
            local_bind = (config['connection'].get('bind_addr', False), config['connection'].get('bind_port', 0))
            if local_bind[0] is False:
                local_bind = False

            self.connections.append(IrcClient(self, name, nick, config=config, channels=config['channels'],
                                              server=server, port=port, use_ssl=config['connection'].get('ssl', False),
                                              local_bind=local_bind))
            logger.debug("[{}] Created connection.".format(name))

    @asyncio.coroutine
    def stop(self, reason=None, *, restart=False):
        """quits all networks and shuts the bot down"""
        logger.info("Stopping bot.")

        if self.config_reloading_enabled:
            logger.debug("Stopping config reloader.")
            self.config.stop()

        for connection in self.connections:
            if not connection.connected:
                # Don't quit a connection that hasn't connected
                continue
            logger.debug("[{}] Closing connection.".format(connection.name))

            connection.quit(reason)

        yield from asyncio.sleep(0.5)  # wait for 'QUIT' calls to take affect

        for connection in self.connections:
            if not connection.connected:
                # Don't close a connection that hasn't connected
                continue
            connection.close()

        self.running = False
        # Give the stopped_future a result, so that run() will exit
        self.stopped_future.set_result(restart)

    @asyncio.coroutine
    def restart(self, reason=None):
        """shuts the bot down and restarts it"""
        yield from self.stop(reason=reason, restart=True)

    @asyncio.coroutine
    def _init_routine(self):
        # Load plugins
        yield from self.plugin_manager.load_all(os.path.abspath("plugins"))

        # If we we're stopped while loading plugins, cancel that and just stop
        if not self.running:
            logger.info("Killed while loading, exiting")
            return

        # Connect to servers
        yield from asyncio.gather(*[conn.connect() for conn in self.connections], loop=self.loop)

        # Run a manual garbage collection cycle, to clean up any unused objects created during initialization
        gc.collect()

    @asyncio.coroutine
    def process(self, event):
        """
        :type event: Event
        """
        try:
            first = []
            tasks = []
            command_prefix = event.conn.config.get('command_prefix', '.')

            # Raw IRC hook
            for raw_hook in self.plugin_manager.catch_all_triggers:
                # run catch-all coroutine hooks before all others - TODO: Make this a plugin argument
                if not raw_hook.threaded:
                    first.append(
                        self.plugin_manager.launch(raw_hook, Event(hook=raw_hook, base_event=event)))
                else:
                    tasks.append(self.plugin_manager.launch(raw_hook, Event(hook=raw_hook, base_event=event)))
            if event.irc_command in self.plugin_manager.raw_triggers:
                for raw_hook in self.plugin_manager.raw_triggers[event.irc_command]:
                    tasks.append(self.plugin_manager.launch(raw_hook, Event(hook=raw_hook, base_event=event)))

            # Event hooks
            if event.type in self.plugin_manager.event_type_hooks:
                for event_hook in self.plugin_manager.event_type_hooks[event.type]:
                    tasks.append(self.plugin_manager.launch(event_hook, Event(hook=event_hook, base_event=event)))

            if event.type is EventType.message:
                # Commands
                if event.chan.lower() == event.nick.lower():  # private message, no command prefix
                    command_re = r'(?i)^(?:[{}]?|{}[,;:]+\s+)(\w+)(?:$|\s+)(.*)'.format(command_prefix, event.conn.nick)
                else:
                    command_re = r'(?i)^(?:[{}]|{}[,;:]+\s+)(\w+)(?:$|\s+)(.*)'.format(command_prefix, event.conn.nick)

                cmd_match = re.match(command_re, event.content)

                if cmd_match:
                    command = cmd_match.group(1).lower()
                    if command in self.plugin_manager.commands:
                        command_hook = self.plugin_manager.commands[command]
                        command_event = CommandEvent(hook=command_hook, text=cmd_match.group(2).strip(),
                                                     triggered_command=command, base_event=event)
                        tasks.append(self.plugin_manager.launch(command_hook, command_event))
                    else:
                        potential_matches = []
                        for potential_match, plugin in self.plugin_manager.commands.items():
                            if potential_match.startswith(command):
                                potential_matches.append((potential_match, plugin))
                        if potential_matches:
                            if len(potential_matches) == 1:
                                command_hook = potential_matches[0][1]
                                command_event = CommandEvent(hook=command_hook, text=cmd_match.group(2).strip(),
                                                             triggered_command=command, base_event=event)
                                tasks.append(self.plugin_manager.launch(command_hook, command_event))
                            else:
                                event.notice("Possible matches: {}".format(
                                    formatting.get_text_list([command for command, plugin in potential_matches])))

                # Regex hooks
                for regex, regex_hook in self.plugin_manager.regex_hooks:
                    if not cmd_match or regex_hook.run_on_cmd:
                        match = regex.search(event.content)
                        if match:
                            regex_event = RegexEvent(hook=regex_hook, match=match, base_event=event)
                            tasks.append(self.plugin_manager.launch(regex_hook, regex_event))

            # Run the tasks
            yield from asyncio.gather(*first, loop=self.loop)
            yield from asyncio.gather(*tasks, loop=self.loop)
        except Exception:
            logger.exception("Error while processing event")
