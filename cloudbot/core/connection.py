from _ssl import PROTOCOL_SSLv23
import asyncio
import re
import ssl
import logging
from ssl import SSLContext

from cloudbot.core.permissions import PermissionManager
from cloudbot.core.events import BaseEvent, EventType

logger = logging.getLogger("cloudbot")

irc_prefix_re = re.compile(r":([^ ]*) ([^ ]*) (.*)")
irc_noprefix_re = re.compile(r"([^ ]*) (.*)")
irc_netmask_re = re.compile(r"([^!@]*)!([^@]*)@(.*)")
irc_param_re = re.compile(r"(?:^|(?<= ))(:.*|[^ ]+)")

irc_command_to_event_type = {
    "PRIVMSG": EventType.message,
    "JOIN": EventType.join,
    "PART": EventType.part,
    "KICK": EventType.kick,
    "NOTICE": EventType.notice
}


class BotConnection:
    """
    A BotConnection represents each connection the bot makes to a single server
    :type bot: cloudbot.core.bot.CloudBot
    :type loop: asyncio.events.AbstractEventLoop
    :type name: str
    :type readable_name: str
    :type channels: list[str]
    :type config: dict[str, unknown]
    :type use_ssl: bool
    :type server: str
    :type port: int
    :type nick: str
    :type vars: dict
    :type history: dict[str, list[tuple]]
    :type permissions: PermissionManager
    :type _connected: bool
    :type _ignore_cert_errors: bool
    """

    def __init__(self, bot, name, server, nick, port=6667, use_ssl=False, channels=None, config=None,
                 readable_name=None, ignore_cert_errors=True, timeout=300):
        """
        :type bot: cloudbot.core.bot.CloudBot
        :type name: str
        :type server: str
        :type nick: str
        :type port: int
        :type use_ssl: bool
        :type channels: list[str]
        :type config: dict[str, unknown]
        """
        self.bot = bot
        self.loop = bot.loop
        self.name = name
        if readable_name:
            self.readable_name = readable_name
        else:
            self.readable_name = name
        if channels is None:
            self.channels = []
        else:
            self.channels = channels

        if config is None:
            self.config = {}
        else:
            self.config = config

        self.use_ssl = use_ssl
        self._ignore_cert_errors = ignore_cert_errors
        self._timeout = timeout
        self.server = server
        self.port = port
        self.nick = nick
        self.vars = {}
        self.history = {}

        # create permissions manager
        self.permissions = PermissionManager(self)

        # create SSL context
        if self.use_ssl:
            self.ssl_context = SSLContext(PROTOCOL_SSLv23)
            if self._ignore_cert_errors:
                self.ssl_context.verify_mode = ssl.CERT_NONE
            else:
                self.ssl_context.verify_mode = ssl.CERT_REQUIRED
        else:
            self.ssl_context = None

        # if we're connected
        self._connected = False
        # if we've quit
        self._quit = False
        # transport and protocol
        self._transport = None
        self._protocol = None

    def describe_server(self):
        if self.use_ssl:
            return "+{}:{}".format(self.server, self.port)
        else:
            return "{}:{}".format(self.server, self.port)

    @asyncio.coroutine
    def connect(self):
        """
        Connects to the IRC server, or reconnects if already connected.
        """
        if self._quit:
            # we've quit, so close instead (because this has probably been called because of EOF received)
            self.close()
            return
        # connect to the irc server
        if self._connected:
            logger.info("[{}] Reconnecting".format(self.readable_name))
            self._transport.close()
        else:
            self._connected = True
            logger.info("[{}] Connecting".format(self.readable_name))

        self._transport, self._protocol = yield from self.loop.create_connection(
            lambda: IRCProtocol(self), host=self.server, port=self.port, ssl=self.ssl_context,
        )

        # send the password, nick, and user
        self.set_pass(self.config["connection"].get("password"))
        self.set_nick(self.nick)
        self.cmd("USER", [self.config.get('user', 'cloudbot'), "3", "*",
                          self.config.get('realname', 'CloudBot - http://git.io/cloudbot')])

    def quit(self, reason=None):
        if self._quit:
            return
        self._quit = True
        if reason:
            self.cmd("QUIT", [reason])
        else:
            self.cmd("QUIT")

    def close(self):
        if not self._connected:
            return
        self._transport.close()
        self._connected = False

    def set_pass(self, password):
        """
        :type password: str
        """
        if password:
            self.cmd("PASS", [password])

    def set_nick(self, nick):
        """
        :type nick: str
        """
        self.cmd("NICK", [nick])

    def join(self, channel):
        """ makes the bot join a channel
        :type channel: str
        """
        self.send("JOIN {}".format(channel))
        if channel not in self.channels:
            self.channels.append(channel)

    def part(self, channel):
        """ makes the bot leave a channel
        :type channel: str
        """
        self.cmd("PART", [channel])
        if channel in self.channels:
            self.channels.remove(channel)

    def msg(self, target, text):
        """ makes the bot send a PRIVMSG to a target
        :type text: str
        :type target: str
        """
        self.cmd("PRIVMSG", [target, text])

    def ctcp(self, target, ctcp_type, text):
        """ makes the bot send a PRIVMSG CTCP to a target
        :type ctcp_type: str
        :type text: str
        :type target: str
        """
        out = "\x01{} {}\x01".format(ctcp_type, text)
        self.cmd("PRIVMSG", [target, out])

    def cmd(self, command, params=None):
        """
        :param command: The IRC command to send
        :param params: The params to the IRC command
        :type command: str
        :type params: list[str]
        """
        if params:
            params[-1] = ':' + params[-1]
            self.send("{} {}".format(command, ' '.join(params)))
        else:
            self.send(command)

    def send(self, line):
        """
        Sends a raw IRC line
        :type line: str
        """
        if not self._connected:
            raise ValueError("Connection must be connected to irc server to use send")
        logger.info("[{}] >> {}".format(self.readable_name, line))
        self.loop.call_soon_threadsafe(asyncio.async, self._protocol.send(line))

    @property
    def connected(self):
        return self._connected


class IRCProtocol(asyncio.Protocol):
    """
    :type loop: asyncio.events.AbstractEventLoop
    :type readable_name: str
    :type describe_server: lambda
    :type conn: BotConnection
    :type bot: cloudbot.core.bot.CloudBot
    :type _input_buffer: bytes
    :type _connected: bool
    :type _transport: asyncio.transports.Transport
    :type _connected_future: asyncio.Future
    """

    def __init__(self, conn):
        """
        :type conn: BotConnection
        """
        self.loop = conn.loop
        self.readable_name = conn.readable_name
        self.describe_server = lambda: conn.describe_server()
        self.conn = conn
        self.bot = conn.bot
        # input buffer
        self._input_buffer = b""

        # connected
        self._connected = False

        # transport
        self._transport = None

        # Future that waits until we are connected
        self._connected_future = asyncio.Future(loop=self.loop)

    def connection_made(self, transport):
        self._transport = transport
        self._connected = True
        self._connected_future.set_result(None)
        # we don't need the _connected_future, everything uses it will check _connected first.
        del self._connected_future

    def connection_lost(self, exc):
        self._connected = False
        # create a new connected_future for when we are connected.
        self._connected_future = asyncio.Future()
        if exc is None:
            # we've been closed intentionally, so don't reconnect
            return
        logger.exception("[{}] Connection lost.".format(self.readable_name))
        asyncio.async(self.conn.connect(), loop=self.loop)

    def eof_received(self):
        self._connected = False
        # create a new connected_future for when we are connected.
        self._connected_future = asyncio.Future()
        logger.info("[{}] EOF received.".format(self.readable_name))
        asyncio.async(self.conn.connect(), loop=self.loop)
        return True

    @asyncio.coroutine
    def send(self, line):
        # make sure we are connected before sending
        if not self._connected:
            yield from self._connected_future
        line = line.splitlines()[0][:500] + "\r\n"
        data = line.encode("utf-8", "replace")
        self._transport.write(data)

    def data_received(self, data):
        self._input_buffer += data

        while b"\r\n" in self._input_buffer:
            line_data, self._input_buffer = self._input_buffer.split(b"\r\n", 1)
            line = line_data.decode()

            # parse the line into a message
            if line.startswith(":"):
                prefix_line_match = irc_prefix_re.match(line)
                if prefix_line_match is None:
                    logger.critical("[{}] Received invalid IRC line '{}' from {}".format(
                        self.readable_name, line, self.describe_server()))
                    continue

                netmask_prefix, command, params = prefix_line_match.groups()
                prefix = ":" + netmask_prefix  # TODO: Do we need to know this?
                netmask_match = irc_netmask_re.match(netmask_prefix)
                if netmask_match is None:
                    # This isn't in the format of a netmask
                    nick = netmask_prefix
                    user = None
                    host = None
                    mask = netmask_prefix
                else:
                    nick = netmask_match.group(1)
                    user = netmask_match.group(2)
                    host = netmask_match.group(3)
                    mask = netmask_prefix
            else:
                prefix = None
                noprefix_line_match = irc_noprefix_re.match(line)
                if noprefix_line_match is None:
                    logger.critical("[{}] Received invalid IRC line '{}' from {}".format(
                        self.readable_name, line, self.describe_server()))
                    continue
                command = noprefix_line_match.group(1)
                params = noprefix_line_match.group(2)
                nick = None
                user = None
                host = None
                mask = None

            command_params = irc_param_re.findall(params)

            # Reply to pings immediately

            if command == "PING":
                asyncio.async(self.send("PONG " + command_params[-1]), loop=self.loop)

            # Parse the command and params

            # Content
            if command_params and command_params[-1].startswith(":"):
                # If the last param is in the format of `:content` remove the `:` from it, and set content from it
                content = command_params[-1][1:]
            else:
                content = None

            # Event type
            if command in irc_command_to_event_type:
                event_type = irc_command_to_event_type[command]
            else:
                event_type = EventType.other

            # Target (for KICK, INVITE)
            if event_type is EventType.kick:
                target = command_params[1]
            elif command == "INVITE":
                target = command_params[0]
            else:
                # TODO: Find more commands which give a target
                target = None

            # Parse for CTCP
            if event_type is EventType.message and content.count("\x01") >= 2 and content.startswith("\x01"):
                # Remove the first \x01, then rsplit to remove the last one, and ignore text after the last \x01
                ctcp_text = content[1:].rsplit("\x01", 1)[0]
                ctcp_text_split = ctcp_text.split(None, 1)
                if ctcp_text_split[0] == "ACTION":
                    # this is a CTCP ACTION, set event_type and content accordingly
                    event_type = EventType.action
                    content = ctcp_text_split[1]
                else:
                    # this shouldn't be considered a regular message
                    event_type = EventType.other
            else:
                ctcp_text = None

            # Channel
            # TODO: Migrate plugins using chan for storage to use chan.lower() instead so we can pass the original case
            if command_params and (len(command_params) > 2 or not command_params[0].startswith(":")):

                if command_params[0].lower() == self.conn.nick.lower():
                    # this is a private message - set the channel to the sender's nick
                    channel = nick.lower()
                else:
                    channel = command_params[0].lower()
            else:
                channel = None

            # Set up parsed message
            # TODO: Do we really want to send the raw `prefix` and `command_params` here?
            event = BaseEvent(bot=self.bot, conn=self.conn, event_type=event_type, content=content, target=target,
                              channel=channel, nick=nick, user=user, host=host, mask=mask, irc_raw=line,
                              irc_prefix=prefix, irc_command=command, irc_paramlist=command_params,
                              irc_ctcp_text=ctcp_text)

            # handle the message, async
            asyncio.async(self.bot.process(event), loop=self.loop)
