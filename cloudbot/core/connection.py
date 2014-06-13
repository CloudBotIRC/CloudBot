from _ssl import PROTOCOL_SSLv23
import asyncio
import re
import ssl
import logging
from ssl import SSLContext

from cloudbot.core.permissions import PermissionManager
from cloudbot.core.events import BaseEvent

logger = logging.getLogger("cloudbot")

irc_prefix_re = re.compile(r":([^ ]*) ([^ ]*) (.*)")
irc_noprefix_re = re.compile(r"([^ ]*) (.*)")
irc_netmask_re = re.compile(r"([^!@]*)!([^@]*)@(.*)")
irc_param_re = re.compile(r"(?:^|(?<= ))(:.*|[^ ]+)")


class BotConnection:
    """ A BotConnection represents each connection the bot makes to an IRC server
    :type bot: cloudbot.core.bot.CloudBot
    :type name: str
    :type channels: list[str]
    :type config: dict[str, unknown]
    :type ssl: bool
    :type server: str
    :type port: int
    :type nick: str
    :type vars: dict
    :type history: dict[str, list[tuple]]
    :type connection: IRCConnection
    :type permissions: PermissionManager
    :type connected: bool
    """

    def __init__(self, bot, name, server, nick, port=6667, use_ssl=False, channels=None, config=None,
                 readable_name=None):
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

        self.ssl = use_ssl
        self.server = server
        self.port = port
        self.nick = nick
        self.vars = {}
        self.history = {}

        # create permissions manager
        self.permissions = PermissionManager(self)

        # create the IRC connection
        self.connection = IRCConnection(self)

        self.connected = False
        # if we've quit
        self._quit = False

    @asyncio.coroutine
    def connect(self):
        """
        Connects to the IRC server. This by itself doesn't start receiving or sending data.
        """
        if self._quit:
            # we've quit, so close instead (because this has probably been called because of EOF received)
            self.connection.close()
            return
        # connect to the irc server
        yield from self.connection.connect()

        self.connected = True

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
        self.connection.close()

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
        if not self.connected:
            raise ValueError("Connection must be connected to irc server to use send")
        logger.info("[{}] >> {}".format(self.readable_name, line))
        self.loop.call_soon_threadsafe(asyncio.async, self.connection.send(line))


class IRCConnection:
    """
    Handles an IRC Connection to a specific IRC server.

    :type logger: logging.Logger
    :type readable_name: str
    :type host: str
    :type port: int
    :type use_ssl: bool
    :type botconn: BotConnection
    :type ignore_cert_errors: bool
    :type timeout: int
    :type _connected: bool
    :type _protocol: IRCProtocol
    """

    def __init__(self, conn, ignore_cert_errors=True, timeout=300):
        """
        :type conn: BotConnection
        """
        self.readable_name = conn.readable_name
        self.host = conn.server
        self.port = conn.port
        self.use_ssl = conn.ssl
        self.loop = conn.loop
        self.botconn = conn

        if self.use_ssl:
            self.ssl_context = SSLContext(PROTOCOL_SSLv23)
            if ignore_cert_errors:
                self.ssl_context.verify_mode = ssl.CERT_NONE
            else:
                self.ssl_context.verify_mode = ssl.CERT_REQUIRED
        else:
            self.ssl_context = None

        self.timeout = timeout
        # Stores if we're connected
        self._connected = False
        # transport and protocol
        self._transport = None
        self._protocol = None

    def describe_server(self):
        if self.use_ssl:
            return "+{}:{}".format(self.host, self.port)
        else:
            return "{}:{}".format(self.host, self.port)

    @asyncio.coroutine
    def connect(self):
        """
        Connects to the irc server
        """
        if self._connected:
            logger.info("[{}] Reconnecting".format(self.readable_name))
            self._transport.close()
        else:
            self._connected = True
            logger.info("[{}] Connecting".format(self.readable_name))

        self._transport, self._protocol = yield from self.loop.create_connection(
            lambda: IRCProtocol(self), host=self.host, port=self.port, ssl=self.ssl_context,
        )

    @asyncio.coroutine
    def send(self, line):
        """
        Sends a raw IRC line to the connected server. If we aren't currently connected to the server, this method will
        pause until we connect.
        :param line: Line to send
        """
        yield from self._protocol.send(line)

    def close(self):
        if not self._connected:
            return
        self._transport.close()
        self._connected = False


class IRCProtocol(asyncio.Protocol):
    def __init__(self, ircconn):
        """
        :type ircconn: IRCConnection
        """
        self.loop = ircconn.loop
        self.readable_name = ircconn.readable_name
        self.describe_server = lambda: ircconn.describe_server()
        self.botconn = ircconn.botconn
        self.bot = ircconn.botconn.bot
        # input buffer
        self._input_buffer = b""
        # connected
        self._connected = False

        # transport
        self.transport = None

        # Future that waits until we are connected
        self._connected_future = asyncio.Future()

    def connection_made(self, transport):
        self.transport = transport
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
        asyncio.async(self.botconn.connect(), loop=self.loop)

    def eof_received(self):
        self._connected = False
        # create a new connected_future for when we are connected.
        self._connected_future = asyncio.Future()
        logger.info("[{}] EOF received.".format(self.readable_name))
        asyncio.async(self.botconn.connect(), loop=self.loop)
        return True

    @asyncio.coroutine
    def send(self, line):
        # make sure we are connected before sending
        if not self._connected:
            yield from self._connected_future
        line = line.splitlines()[0][:500] + "\r\n"
        data = line.encode("utf-8", "replace")
        self.transport.write(data)

    def data_received(self, data):
        self._input_buffer += data
        while b"\r\n" in self._input_buffer:
            line, self._input_buffer = self._input_buffer.split(b"\r\n", 1)
            line = line.decode()

            # parse the line into a message
            if line.startswith(":"):
                prefix_line_match = irc_prefix_re.match(line)
                if prefix_line_match is None:
                    logger.critical("[{}] Received invalid IRC line '{}' from {}".format(
                        self.readable_name, line, self.describe_server()
                    ))
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
                        self.readable_name, line, self.describe_server()
                    ))
                    continue
                command = noprefix_line_match.group(1)
                params = noprefix_line_match.group(2)
                nick = None
                user = None
                host = None
                mask = None

            command_params = irc_param_re.findall(params)

            if command_params:
                # If the last param is in the format of `:message text` remove the `:` from it, so that it is just the content.
                if command_params[-1].startswith(":"):
                    command_params[-1] = command_params[-1][1:]
                irc_message_content = command_params[-1]
            else:
                irc_message_content = None

            # Reply to pings immediately
            if command == "PING":
                asyncio.async(self.send("PONG :" + irc_message_content))

            # Set up parsed message
            # TODO: Do we really want to send the raw `prefix` and `command_params` here?
            event = BaseEvent(conn=self.botconn, irc_raw=line, irc_prefix=prefix, irc_command=command,
                              irc_paramlist=command_params, irc_message=irc_message_content, nick=nick, user=user,
                              host=host,
                              mask=mask)

            # handle the message, async
            asyncio.async(self.bot.process(event))
