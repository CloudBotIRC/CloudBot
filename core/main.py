import asyncio
import re
import _thread
import queue
from queue import Empty
import threading

_thread.stack_size(1024 * 512)  # reduce vm size


class Input:
    """
    :type bot: core.bot.CloudBot
    :type conn: core.irc.BotConnection
    :type raw: str
    :type prefix: str
    :type command: str
    :type params: str
    :type nick: str
    :type user: str
    :type host: str
    :type mask: str
    :type paraml: list[str]
    :type msg: str
    :type input: Input
    :type inp: str | re.__Match
    :type text: str
    :type match: re.__Match
    :type server: str
    :type lastparam: str
    :type chan: str
    """

    def __init__(self, bot=None, conn=None, raw=None, prefix=None, command=None, params=None, nick=None, user=None,
                 host=None, mask=None, paramlist=None, lastparam=None, text=None, match=None, trigger=None):
        """
        :type bot: core.bot.CloudBot
        :type conn: core.irc.BotConnection
        :type raw: str
        :type prefix: str
        :type command: str
        :type params: str
        :type nick: str
        :type user: str
        :type host: str
        :type mask: str
        :type paramlist: list[str]
        :type lastparam: str
        :type text: str
        :type match: re.__Match
        :type trigger: str
        """
        self.bot = bot
        self.conn = conn
        self.raw = raw
        self.prefix = prefix
        self.command = command
        self.params = params
        self.nick = nick
        self.user = user
        self.host = host
        self.mask = mask
        self.paramlist = paramlist
        self.paraml = paramlist
        self.lastparam = lastparam
        self.msg = lastparam
        self.text = text
        self.match = match
        self.trigger = trigger

        self.input = self

        if self.text is not None:
            self.inp = self.text
        elif self.match is not None:
            self.inp = self.match
        else:
            self.inp = self.paramlist

        if self.conn is not None:
            self.server = conn.server
        else:
            self.server = None

        if self.paramlist:
            self.chan = paramlist[0].lower()
        else:
            self.chan = None

        if self.chan is not None and self.nick is not None:
            if self.chan == conn.nick.lower():  # is a PM
                self.chan = self.nick

    def message(self, message, target=None):
        """sends a message to a specific or current channel/user
        :type message: str
        :type target: str
        """
        if target is None:
            if self.chan is None:
                raise ValueError("Target must be specified when chan is not assigned")
            target = self.chan
        self.conn.msg(target, message)

    def reply(self, message, target=None):
        """sends a message to the current channel/user with a prefix
        :type message: str
        :type target: str
        """
        if target is None:
            if self.chan is None:
                raise ValueError("Target must be specified when chan is not assigned")
            target = self.chan

        if target == self.nick:
            self.conn.msg(target, message)
        else:
            self.conn.msg(target, "({}) {}".format(self.nick, message))

    def action(self, message, target=None):
        """sends an action to the current channel/user or a specific channel/user
        :type message: str
        :type target: str
        """
        if target is None:
            if self.chan is None:
                raise ValueError("Target must be specified when chan is not assigned")
            target = self.chan

        self.conn.ctcp(target, "ACTION", message)

    def ctcp(self, message, ctcp_type, target=None):
        """sends an ctcp to the current channel/user or a specific channel/user
        :type message: str
        :type ctcp_type: str
        :type target: str
        """
        if target is None:
            if self.chan is None:
                raise ValueError("Target must be specified when chan is not assigned")
            target = self.chan
        self.conn.ctcp(target, ctcp_type, message)

    def notice(self, message, target=None):
        """sends a notice to the current channel/user or a specific channel/user
        :type message: str
        :type target: str
        """
        if target is None:
            if self.nick is None:
                raise ValueError("Target must be specified when nick is not assigned")
            target = self.nick

        self.conn.cmd('NOTICE', [target, message])

    def has_permission(self, permission, notice=True):
        """ returns whether or not the current user has a given permission
        :type permission: str
        :rtype: bool
        """
        if not self.mask:
            raise ValueError("has_permission requires mask is not assigned")
        return self.conn.permissions.has_perm_mask(self.mask, permission, notice=notice)


def prepare_parameters(bot, plugin, input):
    """
    Prepares arguments for the given plugin

    :type bot: core.bot.CloudBot
    :type plugin: Plugin
    :type input: Input
    :rtype: list
    """
    parameters = []

    # Does the command need DB access?
    uses_db = "db" in plugin.required_args

    if uses_db:
        # create SQLAlchemy session
        bot.logger.debug("Opened database session for {}:{}".format(plugin.module.title, plugin.function_name))
        input.db = input.bot.db_session()

    for required_arg in plugin.required_args:
        if hasattr(input, required_arg):
            value = getattr(input, required_arg)
            parameters.append(value)
        else:
            bot.logger.error("Plugin {}:{} asked for invalid argument '{}', cancelling execution!"
                             .format(plugin.module.title, plugin.function_name, required_arg))
            input.db.close()
            return None

    return parameters


def run_threaded(bot, plugin, input):
    """
    Runs the specific plugin with the given bot and input.

    Returns False if the plugin errored, True otherwise.

    :type bot: core.bot.CloudBot
    :type plugin: Plugin
    :type input: Input
    :rtype: bool
    """
    parameters = prepare_parameters(bot, plugin, input)
    if parameters is None:
        return False
    try:
        out = plugin.function(*parameters)
    except Exception:
        bot.logger.exception("Error in plugin {}:{}:".format(plugin.module.title, plugin.function_name))
        bot.logger.info("Parameters used: {}".format(parameters))
        return False
    else:
        if out is not None:
            input.reply(str(out))
        return True
    finally:
        # ensure that the database session is closed
        if hasattr(input, "db"):
            bot.logger.debug("Closed database session for: {}:{}".format(plugin.module.title, plugin.function_name))
            input.db.close()


@asyncio.coroutine
def run(bot, plugin, input):
    """
    Runs the specific plugin with the given bot and input.

    Returns False if the plugin errored, True otherwise.

    :type bot: core.bot.CloudBot
    :type plugin: Plugin
    :type input: Input
    :rtype: bool
    """
    parameters = prepare_parameters(bot, plugin, input)
    if parameters is None:
        return False
    try:
        out = yield from plugin.function(*parameters)
    except Exception:
        bot.logger.exception("Error in plugin {}:{}({})"
                             .format(plugin.module.title, plugin.function_name, ", ".join(parameters)))
        return False
    else:
        if out is not None:
            input.reply(str(out))
        return True
    finally:
        # ensure that the database session is closed
        if hasattr(input, "db"):
            bot.logger.debug("Closed database session for {}:{}".format(plugin.module.title, plugin.function_name))
            input.db.close()


@asyncio.coroutine
def do_sieve(sieve, bot, input, plugin):
    """
    :type sieve: Plugin
    :type bot: core.bot.CloudBot
    :type input: Input
    :type plugin: Plugin
    :rtype: Input
    """
    try:
        result = yield from sieve.function(bot, input, plugin)
    except Exception:
        bot.logger.exception("Error running sieve {}:{} on {}:{}:".format(
            sieve.module.title, sieve.function_name, plugin.module.title, plugin.function_name
        ))
        return None
    else:
        return result


class Handler(threading.Thread):
    """Runs modules in their own threads (ensures order)
    :type bot: core.bot.CloudBot
    :type plugin: Plugin
    :type input_queue: queue.Queue[Input]
    """

    def __init__(self, bot, plugin):
        """
        :type bot: core.bot.CloudBot
        :type plugin: Plugin
        """
        self.bot = bot
        self.plugin = plugin
        self.input_queue = queue.Queue()
        threading.Thread.__init__(self, name="Handler for {}".format(plugin.module.title))
        self.start()

    def run(self):
        while True:
            while self.bot.running:  # This loop will break when successful
                try:
                    plugin_input = self.input_queue.get(block=True, timeout=1)
                    break
                except Empty:
                    pass

            if not self.bot.running or plugin_input == StopIteration:
                break

            run_threaded(self.bot, self.plugin, plugin_input)

    def stop(self):
        self.input_queue.put(StopIteration)

    def put(self, value):
        """
        :type value: Input
        """
        self.input_queue.put(value)


@asyncio.coroutine
def dispatch(bot, input, plugin):
    """
    Dispatch a given input to a given plugin using a given bot object. This will either run sync or threaded, depending
    on the plugin's arguments.

    Returns False if the plugin isn't threaded, and the plugin didn't run successfully.
    True if the plugin is threaded, and/or if it ran successfully.

    :type bot: core.bot.CloudBot
    :type input: Input
    :type plugin: core.pluginmanager.Plugin
    :rtype: bool
    """
    if plugin.type != "onload":  # we don't need sieves on onload hooks.
        for sieve in bot.plugin_manager.sieves:
            input = yield from do_sieve(sieve, bot, input, plugin)
            if input is None:
                return False

    if plugin.type == "command" and plugin.auto_help and not input.text:
        if plugin.doc is not None:
            input.notice(input.conn.config["command_prefix"] + plugin.doc)
        else:
            input.notice(input.conn.config["command_prefix"] + plugin.name + " requires additional arguments.")
        return False

    if plugin.threaded:
        if plugin.single_thread:
            if plugin.module.title in bot.handlers:
                bot.handlers[plugin.module.title].put(input)
            else:
                bot.handlers[plugin.module.title] = Handler(bot, plugin)
        else:
            threading.Thread(
                name="Plugin thread for {}".format(plugin.module.title),
                target=run_threaded,
                args=(bot, plugin, input)
            ).start()
    else:
        success = yield from run(bot, plugin, input)
        return success

    # the plugin is threaded, so just return true.
    return True


@asyncio.coroutine
def main(bot, input_params):
    """
    :type bot: core.bot.CloudBot
    :type input_params: dict[str, core.irc.BotConnection | str | list[str]]
    """
    inp = Input(bot=bot, **input_params)
    command_prefix = input_params["conn"].config.get('command_prefix', '.')

    # EVENTS
    if inp.command in bot.plugin_manager.events:
        for event_plugin in bot.plugin_manager.events[inp.command]:
            yield from dispatch(bot, Input(bot=bot, **input_params), event_plugin)
    for event_plugin in bot.plugin_manager.catch_all_events:
        yield from dispatch(bot, Input(bot=bot, **input_params), event_plugin)

    if inp.command == 'PRIVMSG':
        # COMMANDS
        if inp.chan == inp.nick:  # private message, no command prefix
            prefix = '^(?:[{}]?|'.format(command_prefix)
        else:
            prefix = '^(?:[{}]|'.format(command_prefix)
        command_re = prefix + inp.conn.nick
        command_re += r'[,;:]+\s+)(\w+)(?:$|\s+)(.*)'

        match = re.match(command_re, inp.lastparam)

        if match:
            command = match.group(1).lower()
            if command in bot.plugin_manager.commands:
                plugin = bot.plugin_manager.commands[command]
                input = Input(bot=bot, text=match.group(2).strip(), trigger=command, **input_params)
                yield from dispatch(bot, input, plugin)

        # REGEXES
        for regex, plugin in bot.plugin_manager.regex_plugins:
            match = regex.search(inp.lastparam)
            if match:
                input = Input(bot=bot, match=match, **input_params)
                yield from dispatch(bot, input, plugin)
