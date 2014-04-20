import inspect
import re

import _thread
import queue
from queue import Empty

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
    :type text: list[str]
    :type server: str
    :type lastparam: str
    :type chan: str
    """

    def __init__(self, bot, conn, raw, prefix, command, params,
                 nick, user, host, mask, paramlist, msg):
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
        :type msg: str
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
        self.paraml = paramlist
        self.msg = msg
        self.input = self
        self.text = self.paraml
        self.inp = self.paraml  # this is just text with a different name
        self.server = conn.server
        self.lastparam = paramlist[-1]  # TODO: This is equivalent to msg
        self.chan = paramlist[0].lower()

        if self.chan == conn.nick.lower():  # is a PM
            self.chan = nick

        self.trigger = None  # assigned later?

    def message(self, message, target=None):
        """sends a message to a specific or current channel/user
        :type message: str
        :type target: str
        """
        if target is None:
            target = self.chan
        self.conn.msg(target, message)

    def reply(self, message, target=None):
        """sends a message to the current channel/user with a prefix
        :type message: str
        :type target: str
        """
        if target is None:
            target = self.chan

        if target == self.nick:
            self.conn.msg(target, message)
        else:
            self.conn.msg(target, "{}, {}".format(self.nick, message))

    def action(self, message, target=None):
        """sends an action to the current channel/user or a specific channel/user
        :type message: str
        :type target: str
        """
        if target is None:
            target = self.chan

        self.conn.ctcp(target, "ACTION", message)

    def ctcp(self, message, ctcp_type, target=None):
        """sends an ctcp to the current channel/user or a specific channel/user
        :type message: str
        :type ctcp_type: str
        :type target: str
        """
        if target is None:
            target = self.chan
        self.conn.ctcp(target, ctcp_type, message)

    def notice(self, message, target=None):
        """sends a notice to the current channel/user or a specific channel/user
        :type message: str
        :type target: str
        """
        if target is None:
            target = self.nick

        self.conn.cmd('NOTICE', [target, message])

    def has_permission(self, permission):
        """ returns whether or not the current user has a given permission
        :type permission: str
        :rtype: bool
        """
        return self.conn.permissions.has_perm_mask(self.mask, permission)


def run(bot, func, input):
    """
    :type bot: core.bot.CloudBot
    :type func: func
    :type input: Input
    """
    bot.logger.debug("Input: {}".format(input.__dict__))

    parameters = []
    specifications = inspect.getargspec(func)
    required_args = specifications[0]
    if required_args is None:
        required_args = []

    # Does the command need DB access?
    uses_db = "db" in required_args

    if uses_db:
        # create SQLAlchemy session
        bot.logger.debug("Opened DB session for: {}".format(func._filename))
        input.db = input.bot.db_session()

    # all the dynamic arguments
    for required_arg in required_args:
        if hasattr(input, required_arg):
            value = getattr(input, required_arg)
            parameters.append(value)
        else:
            bot.logger.warning(
                "Plugin {} asked for invalid argument '{}', setting it to None".format(func._filename, required_arg))
            parameters.append(None)
    try:
        out = func(*parameters)
    except:
        bot.logger.exception("Error in plugin {}:".format(func._filename))
        bot.logger.info("Parameters used: {}".format(parameters))
        return
    finally:
        if uses_db:
            bot.logger.debug("Closed DB session for: {}".format(func._filename))
            input.db.close()

    if out is not None:
        input.reply(str(out))


def do_sieve(sieve, bot, input, func, type, args):
    """
    :type sieve: function
    :type bot: core.bot.CloudBot
    :type input: Input
    :type func: function
    :type type: str
    :type args: dict[str, ?]
    :rtype: Input
    """
    try:
        return sieve(bot, input, func, type, args)
    except:
        bot.logger.exception("Error in sieve {}:".format(func._filename))
        return None


class Handler:
    """Runs plugins in their own threads (ensures order)
    :type bot: core.bot.CloudBot
    :type func: function
    :type input_queue: queue.Queue[Input]
    """

    def __init__(self, bot, func):
        """
        :type bot: core.bot.CloudBot
        :type func: function
        """
        self.bot = bot
        self.func = func
        self.input_queue = queue.Queue()
        _thread.start_new_thread(self.start, ())

    def start(self):
        uses_db = True
        while True:
            while self.bot.running:  # This loop will break when successful
                try:
                    input = self.input_queue.get(block=True, timeout=1)
                    break
                except Empty:
                    pass

            if not self.bot.running or input == StopIteration:
                break

            run(self.bot, self.func, input)

    def stop(self):
        self.input_queue.put(StopIteration)

    def put(self, value):
        """
        :type value: Input
        """
        self.input_queue.put(value)


def dispatch(bot, input, kind, func, args, autohelp=False):
    """
    :type bot: core.bot.CloudBot
    :type input: Input
    :type kind: str
    :type func: function
    :type args: dict[str, ?]
    :type autohelp: bool
    """
    for sieve, in bot.plugins['sieve']:
        input = do_sieve(sieve, bot, input, func, kind, args)
        if input is None:
            return

    if autohelp and args.get('autohelp', True) and not input.text and func.__doc__ is not None:
        input.notice(input.conn.config["command_prefix"] + func.__doc__.split('\n', 1)[0])
        return

    if func._thread:
        bot.threads[func].put(input)
    else:
        _thread.start_new_thread(run, (bot, func, input))


def match_command(bot, command):
    """
    :type bot: core.bot.CloudBot
    :type command: str
    :rtype: str | list
    """
    commands = list(bot.commands)

    # do some fuzzy matching
    prefix = [x for x in commands if x.startswith(command)]
    if len(prefix) == 1:
        return prefix[0]
    elif prefix and command not in prefix:
        return prefix

    return command


def main(bot, conn, out):
    """
    :type bot: core.bot.CloudBot
    :type conn: core.irc.BotConnection
    :type out: list
    """
    inp = Input(bot, conn, *out)
    command_prefix = conn.config.get('command_prefix', '.')

    # EVENTS
    for func, args in bot.events[inp.command] + bot.events['*']:
        dispatch(bot, Input(bot, conn, *out), "event", func, args)

    if inp.command == 'PRIVMSG':
        # COMMANDS
        if inp.chan == inp.nick:  # private message, no command prefix
            prefix = '^(?:[{}]?|'.format(command_prefix)
        else:
            prefix = '^(?:[{}]|'.format(command_prefix)
        command_re = prefix + inp.conn.nick
        command_re += r'[,;:]+\s+)(\w+)(?:$|\s+)(.*)'

        m = re.match(command_re, inp.lastparam)

        if m:
            trigger = m.group(1).lower()
            command = match_command(bot, trigger)

            if isinstance(command, list):  # multiple potential matches
                input = Input(bot, conn, *out)
                input.notice("Did you mean {} or {}?".format
                             (', '.join(command[:-1]), command[-1]))
            elif command in bot.commands:
                input = Input(bot, conn, *out)
                input.trigger = trigger
                input.text_unstripped = m.group(2)
                input.text = input.text_unstripped.strip()
                input.inp = input.text

                func, args = bot.commands[command]
                dispatch(bot, input, "command", func, args, autohelp=True)

        # REGEXES
        for func, args in bot.plugins['regex']:
            m = args['re'].search(inp.lastparam)
            if m:
                input = Input(bot, conn, *out)
                input.text = m
                input.inp = m

                dispatch(bot, input, "regex", func, args)
