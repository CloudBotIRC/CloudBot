import asyncio
import re
import socket
import ssl
import time
from ssl import SSLError

from core.permissions import PermissionManager

irc_prefix_re = re.compile(r":([^ ]*) ([^ ]*) (.*)")
irc_noprefix_re = re.compile(r"([^ ]*) (.*)")
irc_netmask_re = re.compile(r"([^!@]*)!([^@]*)@(.*)")
irc_param_re = re.compile(r"(?:^|(?<= ))(:.*|[^ ]+)")


class BotConnection:
    """ A BotConnection represents each connection the bot makes to an IRC server
    :type bot: core.bot.CloudBot
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
        :type bot: core.bot.CloudBot
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

        self.message_queue = bot.queued_messages  # global parsed message queue, for parsed recieved messages

        self.input_queue = asyncio.Queue()
        self.output_queue = asyncio.Queue()

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

    @asyncio.coroutine
    def run(self):
        """
        Runs this connection's send and receive loops.
        """
        asyncio.async(self.connection.send_loop())
        asyncio.async(self.connection.receive_loop())

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
        self.output_queue.put(string)


class IRCConnection:
    """
    Handles an IRC Connection to a specific IRC server.

    :type logger: logging.Logger
    :type readable_name: str
    :type host: str
    :type port: int
    :type ssl: bool
    :type output_queue: asyncio.Queue
    :type message_queue: asyncio.Queue
    :type botconn: BotConnection
    :type ignore_cert_errors: bool
    :type timeout: int
    :type socket: socket.socket
    :type _input_buffer: bytes
    :type _connected: bool
    :type _stopped: bool
    :type _last_received: int
    """

    def __init__(self, conn, ignore_cert_errors=True, timeout=300):
        """
        :type conn: BotConnection
        """
        self.logger = conn.logger
        self.readable_name = conn.readable_name
        self.host = conn.server
        self.port = conn.port
        self.ssl = conn.ssl
        self.output_queue = conn.output_queue  # lines to be sent out
        self.message_queue = conn.message_queue  # global queue for parsed lines that were recieved
        self.loop = conn.loop
        self.botconn = conn

        self.ignore_cert_errors = ignore_cert_errors
        self.timeout = timeout
        # to be started in connect()
        self.socket = None
        # input buffer
        self._input_buffer = b""
        # Are we connected?
        self._connected = False
        # Have we been stopped?
        self._stopped = False
        # Last time data was received
        self._last_received = 0

    def create_socket(self):
        sock = socket.socket(socket.AF_INET, socket.TCP_NODELAY)
        if self.ssl:
            if self.ignore_cert_errors:
                cert_requirement = ssl.CERT_NONE
            else:
                cert_requirement = ssl.CERT_REQUIRED
            sock = ssl.wrap_socket(sock, server_side=False, cert_reqs=cert_requirement)
        return sock

    def describe_server(self):
        if self.ssl:
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
            self.socket.close()
        else:
            self._connected = True
            self.logger.info("[{}] Connecting".format(self.readable_name))
        self.socket = self.create_socket()
        # reset input buffer
        self._input_buffer = b""
        try:
            addresses = yield from self.loop.getaddrinfo(self.host, self.port)
            address = addresses[0][-1]  # Get the host/port pair
            print("Connecting to {}".format(address))
            yield from self.loop.sock_connect(self.socket, address)
        except socket.error:
            self.logger.warning("Failed to connect to {}".format(self.describe_server()))
            raise

    def stop(self):
        if not self._connected:
            return
        self.socket.close()
        self._connected = False
        self._stopped = True

    @asyncio.coroutine
    def send_loop(self):
        print("Staring send loop for {}".format(self.readable_name))
        while not self._stopped:
            to_send = yield from self.output_queue.get()
            line = to_send.splitlines()[0][:500] + "\r\n"
            data = line.encode("utf-8", "replace")
            yield from self.loop.sock_sendall(self.socket, data)

    @asyncio.coroutine
    def receive_loop(self):
        print("Starting receive loop for {}".format(self.readable_name))
        self._last_received = time.time()
        while not self._stopped:
            try:
                data = yield from self.loop.sock_recv(self.socket, 4096)
            except socket.timeout:
                # Reconnect to the server
                self.logger.exception("[{}] Got timeout receiving data from {}".format(
                    self.readable_name, self.describe_server()))
                yield from self.botconn.connect()
                continue
            except (SSLError, socket.error):
                if self._stopped:
                    return  # The error is most likely caused by stopping & closing the socket
                self.logger.exception("[{}] Error receiving data from {}".format(
                    self.readable_name, self.describe_server()))
                continue

            if not data:
                # TODO: I think this only happens if the socket was closed. Shouldn't we automatically reconnect here?
                if time.time() > self._last_received + self.timeout:
                    # Reconnect to the server
                    yield from self.botconn.connect()
                    continue

            self._last_received = time.time()

        while b"\r\n" in self._input_buffer:
            line, self._input_buffer = self._input_buffer.split(b"\r\n")
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
                    # TODO: This nick, user, host & mask behavior is legacy
                    # What should we actually set them to when netmask_prefix is something like 'irc.znc.in'?
                    nick = netmask_prefix
                    user = ""
                    host = ""
                    mask = "{}!@".format(netmask_prefix)
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
                # TODO: This nick, user, host & mask behavior is legacy
                # What should we do about it?
                nick = ""
                user = ""
                host = ""
                mask = "!@"

            param_list = irc_param_re.findall(params)
            if param_list:
                # TODO: What the heck?
                if param_list[-1].startswith(":"):
                    param_list[-1] = param_list[-1][1:]
                last_param = param_list[-1]
            else:
                last_param = ""  # TODO: Should we set this to None?
            # Set up parsed message
            # TODO: What do you actually want to send here? Are prefix and params really necessary?
            message = {
                "conn": self.botconn, "raw": line, "command": command, "nick": nick, "user": user, "host": host,
                "mask": mask, "paramlist": param_list, "lastparam": last_param,
                "params": params, "prefix": prefix,
            }

            # we should also remember to ping the server if they ping us
            if command == "PING":
                self.output_queue.put("PONG :" + param_list[0])  # TODO: Are we assuming that the ':' as been stripped?

            # Put the message into the queue to be handled
            # TODO: Do we want to directly call the handling method here?
            self.message_queue.put(message)