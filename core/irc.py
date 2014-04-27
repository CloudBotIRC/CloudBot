from _ssl import SSLError
import re
import socket
import time
import threading
import queue
from ssl import wrap_socket, CERT_NONE, CERT_REQUIRED

from core.permissions import PermissionManager

irc_prefix_rem = re.compile(r'(.*?) (.*?) (.*)').match
irc_noprefix_rem = re.compile(r'()(.*?) (.*)').match
irc_netmask_rem = re.compile(r':?([^!@]*)!?([^@]*)@?(.*)').match
irc_param_ref = re.compile(r'(?:^|(?<= ))(:.*|[^ ]+)').findall


def decode(encoded):
    for codec in ('utf-8', 'iso-8859-1', 'shift_jis', 'cp1252'):
        try:
            return encoded.decode(codec)
        except UnicodeDecodeError:
            continue
    return encoded.decode('utf-8', 'ignore')


def censor(text):
    return text


class ReceiveThread(threading.Thread):
    """
    Receives messages from IRC, parses them, and puts them into parsed_queue

    :type input_buffer: bytes
    :type socket: socket.socket
    :type timeout: int
    :type logger: logging.Logger
    :type readable_name: str
    :type output_queue: queue.Queue
    :type message_queue: queue.Queue
    :type botconn: BotConnection
    :type shutdown: bool
    """

    def __init__(self, ircconn):
        """
        :type ircconn: IRCConnection
        """
        self.input_buffer = b""
        self.socket = ircconn.socket
        self.timeout = ircconn.timeout
        self.logger = ircconn.logger
        self.readable_name = ircconn.readable_name
        self.output_queue = ircconn.output_queue
        self.message_queue = ircconn.message_queue
        self.botconn = ircconn.botconn

        self.shutdown = False
        threading.Thread.__init__(self)

    def recv_from_socket(self, nbytes):
        return self.socket.recv(nbytes)

    def handle_receive_exception(self, error, last_timestamp):
        if time.time() - last_timestamp > self.timeout:
            self.message_queue.put({"conn": self.botconn, "reconnect": True})
            self.socket.close()
            return True
        return False

    def run(self):
        last_timestamp = time.time()
        while not self.shutdown:
            try:
                data = self.recv_from_socket(4096)
                self.input_buffer += data
                if data:
                    last_timestamp = time.time()
                else:
                    if time.time() - last_timestamp > self.timeout:
                        self.message_queue.put({"conn": self.botconn, "reconnect": True})
                        self.socket.close()
                        return
                    time.sleep(1)
            except (SSLError, socket.timeout, socket.error) as e:
                if self.handle_receive_exception(e, last_timestamp):
                    return
                continue

            while b'\r\n' in self.input_buffer:
                line, self.input_buffer = self.input_buffer.split(b'\r\n', 1)
                msg = decode(line)
                self.logger.debug("[{}][Raw] {}".format(self.readable_name, msg))

                # parse the message
                if msg.startswith(":"):  # has a prefix
                    prefix, command, params = irc_prefix_rem(msg).groups()
                else:
                    prefix, command, params = irc_noprefix_rem(msg).groups()
                nick, user, host = irc_netmask_rem(prefix).groups()
                mask = nick + "!" + user + "@" + host
                paramlist = irc_param_ref(params)
                lastparam = ""
                if paramlist:
                    if paramlist[-1].startswith(':'):
                        paramlist[-1] = paramlist[-1][1:]
                    lastparam = paramlist[-1]
                # put the parsed message in the response queue
                self.message_queue.put({
                    "conn": self.botconn, "raw": msg, "prefix": prefix, "command": command, "params": params,
                    "nick": nick, "user": user, "host": host, "mask": mask, "paramlist": paramlist,
                    "lastparam": lastparam
                })
                # if the server pings us, pong them back
                if command == "PING":
                    string = "PONG :" + paramlist[0]
                    self.output_queue.put(string)


class SendThread(threading.Thread):
    """sends messages from output_queue to IRC
    :type output_queue: queue.Queue
    :type socket: socket.socket
    :type shutdown: bool
    """

    def __init__(self, sock, output_queue):
        self.output_queue = output_queue
        self.socket = sock

        self.shutdown = False
        threading.Thread.__init__(self)

    def run(self):
        while not self.shutdown:
            line = self.output_queue.get().splitlines()[0][:500]
            encoded = line.encode('utf-8', 'replace') + b'\r\n'
            self.socket.sendall(encoded)


class IRCConnection(object):
    """handles an IRC connection
    :type logger: logging.Logger
    :type conn_name: str
    :type readable_name: str
    :type host: str
    :type port: int
    :type ssl: bool
    :type output_queue: queue.Queue
    :type message_queue: queue.Queue
    :type botconn: BotConnection
    :type ignore_cert_errors: bool
    :type timeout: int
    :type socket: socket.socket
    :type receive_thread: ReceiveThread
    :type send_thread: SendThread
    """

    def __init__(self, conn, ignore_cert_errors=True, timeout=300):
        """
        :type conn: BotConnection
        """
        self.logger = conn.logger
        self.conn_name = conn.name
        self.readable_name = conn.readable_name
        self.host = conn.server
        self.port = conn.port
        self.ssl = conn.ssl
        self.output_queue = conn.output_queue  # lines to be sent out
        self.message_queue = conn.message_queue  # global queue for parsed lines that were recieved
        self.botconn = conn

        self.ignore_cert_errors = ignore_cert_errors
        self.timeout = timeout
        self.socket = self.create_socket()
        # to be started in connect()
        self.receive_thread = ReceiveThread(self)
        self.send_thread = SendThread(self.socket, self.output_queue)

    def create_socket(self):
        sock = socket.socket(socket.AF_INET, socket.TCP_NODELAY)
        if self.ssl:
            if self.ignore_cert_errors:
                cert_requirement = CERT_NONE
            else:
                cert_requirement = CERT_REQUIRED
            sock = wrap_socket(sock, server_side=False, cert_reqs=cert_requirement)

        return sock

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
        except socket.error:
            if self.ssl:
                self.logger.warning("Failed to connect to +{}:{}".format(self.host, self.port))
            else:
                self.logger.warning("Failed to connect to {}:{}".format(self.host, self.port))
            raise

        self.send_thread.start()

    def start_parsing(self):
        self.receive_thread.start()

    def stop(self):
        self.send_thread.shutdown = True
        self.receive_thread.shutdown = True
        time.sleep(0.1)
        self.socket.close()

    def reconnect(self):
        self.stop()
        self.socket = self.create_socket()
        self.connect()


class BotConnection(object):
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
    :type parsed_queue: queue.Queue
    :type input_queue: queue.Queue
    :type output_queue: queue.Queue
    :type connection: IRCConnection
    :type permissions: PermissionManager
    :type connected: bool
    """

    def __init__(self, bot, name, server, nick, port=6667, ssl=False, logger=None, channels=None, config=None,
                 readable_name=None):
        """
        :type bot: core.bot.CloudBot
        :type name: str
        :type server: str
        :type nick: str
        :type port: int
        :type ssl: bool
        :type logger: logging.Logger
        :type channels: list[str]
        :type config: dict[str, unknown]
        """
        self.bot = bot
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

        self.ssl = ssl
        self.server = server
        self.port = port
        self.logger = logger
        self.nick = nick
        self.vars = {}
        self.history = {}

        self.message_queue = bot.queued_messages  # global parsed message queue, for parsed recieved messages

        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()

        # create permissions manager
        self.permissions = PermissionManager(self)

        # create the IRC connection
        self.connection = IRCConnection(self)

        self.connected = False

    def connect(self):
        # connect to the irc server
        self.connection.connect()

        self.connected = True

        # send the password, nick, and user
        self.set_pass(self.config["connection"].get("password"))
        self.set_nick(self.nick)
        self.cmd("USER", [self.config.get('user', 'cloudbot'), "3", "*",
                          self.config.get('realname', 'CloudBot - http://git.io/cloudbot')])

        # start the parse thread
        self.connection.start_parsing()

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
