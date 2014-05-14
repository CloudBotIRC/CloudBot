from _ssl import PROTOCOL_SSLv23
import asyncio
import re
import ssl
from ssl import SSLContext

from .permissions import PermissionManager

from .events import BaseEvent

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
    :type logger: logging.Logger
    :type nick: str
    :type vars: dict
    :type history: dict[str, list[tuple]]
    :type message_queue: queue.Queue
    :type input_queue: queue.Queue
    :type output_queue: queue.Queue
    :type connection: IRCConnection
    :type permissions: PermissionManager
    :type connected: bool
    """

    def __init__(self, bot, name, server, nick, port=6667, use_ssl=False, logger=None, channels=None, config=None,
                 readable_name=None):
        """
        :type bot: cloudbot.core.bot.CloudBot
        :type name: str
        :type server: str
        :type nick: str
        :type port: int
        :type use_ssl: bool
        :type logger: logging.Logger
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
        self.logger = logger
        self.nick = nick
        self.vars = {}
        self.history = {}

        self.message_queue = bot.queued_events  # global parsed message queue, for parsed received messages

        self.input_queue = asyncio.Queue(loop=self.loop)
        self.output_queue = asyncio.Queue(loop=self.loop)

        # create permissions manager
        self.permissions = PermissionManager(self)

        # create the IRC connection
        self.connection = IRCConnection(self)

        self.connected = False

    @asyncio.coroutine
    def connect(self):
        """
        Connects to the IRC server. This by itself doesn't start receiving or sending data.
        """
        # connect to the irc server
        yield from self.connection.connect()

        self.connected = True

        # send the password, nick, and user
        self.set_pass(self.config["connection"].get("password"))
        self.set_nick(self.nick)
        self.cmd("USER", [self.config.get('user', 'cloudbot'), "3", "*",
                          self.config.get('realname', 'CloudBot - http://git.io/cloudbot')])

    def stop(self):
        self.connection.stop()

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

    def send(self, string):
        """
        :type string: str
        """
        if not self.connected:
            raise ValueError("Connection must be connected to irc server to use send")
        self.logger.info("[{}] >> {}".format(self.readable_name, string))
        self.loop.call_soon_threadsafe(asyncio.async, self.output_queue.put(string))


class IRCConnection:
    """
    Handles an IRC Connection to a specific IRC server.

    :type logger: logging.Logger
    :type readable_name: str
    :type host: str
    :type port: int
    :type use_ssl: bool
    :type output_queue: asyncio.Queue
    :type message_queue: asyncio.Queue
    :type botconn: BotConnection
    :type ignore_cert_errors: bool
    :type timeout: int
    :type _connected: bool
    """

    def __init__(self, conn, ignore_cert_errors=True, timeout=300):
        """
        :type conn: BotConnection
        """
        self.logger = conn.logger
        self.readable_name = conn.readable_name
        self.host = conn.server
        self.port = conn.port
        self.use_ssl = conn.ssl
        self.output_queue = conn.output_queue  # lines to be sent out
        self.message_queue = conn.message_queue  # global queue for parsed lines that were received
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
            self.logger.info("[{}] Reconnecting".format(self.readable_name))
            self._transport.close()
        else:
            self._connected = True
            self.logger.info("[{}] Connecting".format(self.readable_name))

        self._transport, self._protocol = yield from self.loop.create_connection(
            lambda: IRCProtocol(self), host=self.host, port=self.port, ssl=self.ssl_context,
        )

    def stop(self):
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
        self.logger = ircconn.logger
        self.readable_name = ircconn.readable_name
        self.describe_server = lambda: ircconn.describe_server()
        self.botconn = ircconn.botconn
        self.output_queue = ircconn.output_queue
        self.message_queue = ircconn.message_queue
        # input buffer
        self._input_buffer = b""
        # connected
        self._connected = False

        # transport
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        self._connected = True
        asyncio.async(self.send_loop(), loop=self.loop)

    def connection_lost(self, exc):
        self._connected = False
        if exc is None:
            # we've been closed intentionally, so don't reconnect
            return
        self.logger.exception("[{}] Connection lost.".format(self.readable_name))
        asyncio.async(self.botconn.connect(), loop=self.loop)

    def eof_received(self):
        self._connected = False
        self.logger.info("[{}] EOF Received, reconnecting.".format(self.readable_name))
        asyncio.async(self.botconn.connect(), loop=self.loop)
        return True

    @asyncio.coroutine
    def send_loop(self):
        while self._connected:
            to_send = yield from self.output_queue.get()
            line = to_send.splitlines()[0][:500] + "\r\n"
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
                    self.logger.critical("[{}] Received invalid IRC line '{}' from {}".format(
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
                    self.logger.critical("[{}] Received invalid IRC line '{}' from {}".format(
                        self.readable_name, line, self.describe_server()
                    ))
                    continue
                command = noprefix_line_match.group(1)
                params = noprefix_line_match.group(2)
                nick = None
                user = None
                host = None
                mask = None

            param_list = irc_param_re.findall(params)
            if param_list:
                # TODO: What the heck?
                if param_list[-1].startswith(":"):
                    param_list[-1] = param_list[-1][1:]
                last_param = param_list[-1]
            else:
                last_param = None
            # Set up parsed message
            # TODO: What do you actually want to send here? Are prefix and params really necessary?
            event = BaseEvent(conn=self.botconn, irc_raw=line, irc_prefix=prefix, irc_command=command,
                              irc_paramlist=param_list, irc_message=last_param, nick=nick, user=user, host=host,
                              mask=mask)
            # we should also remember to ping the server if they ping us
            if command == "PING":
                self.output_queue.put_nowait("PONG :" + last_param)

            # Put the message into the queue to be handled
            # TODO: Do we want to directly call the handling method here?
            self.message_queue.put_nowait(event)
