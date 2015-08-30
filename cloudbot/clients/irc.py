from _ssl import PROTOCOL_SSLv23
import asyncio
import re
import ssl
import logging
from ssl import SSLContext

from cloudbot.client import Client
from cloudbot.event import Event, EventType

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


def decode(bytestring):
    """
    Tries to decode a bytestring using multiple encoding formats
    """
    for codec in ('utf-8', 'iso-8859-1', 'shift_jis', 'cp1252'):
        try:
            return bytestring.decode(codec)
        except UnicodeDecodeError:
            continue
    return bytestring.decode('utf-8', errors='ignore')


class IrcClient(Client):
    """
    An implementation of Client for IRC.
    :type use_ssl: bool
    :type server: str
    :type port: int
    :type _connected: bool
    :type _ignore_cert_errors: bool
    """

    def __init__(self, bot, name, nick, *, channels=None, config=None,
                 server, port=6667, use_ssl=False, ignore_cert_errors=True, timeout=300, local_bind=False):
        """
        :type bot: cloudbot.bot.CloudBot
        :type name: str
        :type nick: str
        :type channels: list[str]
        :type config: dict[str, unknown]
        :type server: str
        :type port: int
        :type use_ssl: bool
        :type ignore_cert_errors: bool
        :type timeout: int
        """
        super().__init__(bot, name, nick, channels=channels, config=config)

        self.use_ssl = use_ssl
        self._ignore_cert_errors = ignore_cert_errors
        self._timeout = timeout
        self.server = server
        self.port = port
        self.local_bind = local_bind
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
        # connect to the clients server
        if self._quit:
            # we've quit, so close instead (because this has probably been called because of EOF received)
            self.close()
            return

        if self._connected:
            logger.info("[{}] Reconnecting".format(self.name))
            self._transport.close()
        else:
            self._connected = True
            logger.info("[{}] Connecting".format(self.name))
        optional_params = {}
        if self.local_bind:
            optional_params["local_addr"] = self.local_bind
        self._transport, self._protocol = yield from self.loop.create_connection(
            lambda: _IrcProtocol(self), host=self.server, port=self.port, ssl=self.ssl_context, **optional_params)

        # send the password, nick, and user
        self.set_pass(self.config["connection"].get("password"))
        self.set_nick(self.nick)
        self.cmd("USER", self.config.get('user', 'cloudbot'), "3", "*",
                 self.config.get('realname', 'CloudBot - https://git.io/CloudBot'))

    def quit(self, reason=None):
        if self._quit:
            return
        self._quit = True
        if reason:
            self.cmd("QUIT", reason)
        else:
            self.cmd("QUIT")

    def close(self):
        if not self._quit:
            self.quit()
        if not self._connected:
            return

        self._transport.close()
        self._connected = False

    def message(self, target, *messages):
        for text in messages:
            text = text.replace("\n", "").replace("\r", "")
            self.cmd("PRIVMSG", target, text)

    def action(self, target, text):
        text = text.replace("\n", "").replace("\r", "")
        self.ctcp(target, "ACTION", text)

    def notice(self, target, text):
        text = text.replace("\n", "").replace("\r", "")
        self.cmd("NOTICE", target, text)

    def set_nick(self, nick):
        self.cmd("NICK", nick)

    def join(self, channel):
        self.send("JOIN {}".format(channel))
        if channel not in self.channels:
            self.channels.append(channel)

    def part(self, channel):
        self.cmd("PART", channel)
        if channel in self.channels:
            self.channels.remove(channel)

    def set_pass(self, password):
        if not password:
            return
        self.cmd("PASS", password)

    def ctcp(self, target, ctcp_type, text):
        """
        Makes the bot send a PRIVMSG CTCP of type <ctcp_type> to the target
        :type ctcp_type: str
        :type text: str
        :type target: str
        """
        out = "\x01{} {}\x01".format(ctcp_type, text)
        self.cmd("PRIVMSG", target, out)

    def cmd(self, command, *params):
        """
        Sends a raw IRC command of type <command> with params <params>
        :param command: The IRC command to send
        :param params: The params to the IRC command
        :type command: str
        :type params: (str)
        """
        params = list(params)  # turn the tuple of parameters into a list
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
            raise ValueError("Client must be connected to irc server to use send")
        self.loop.call_soon_threadsafe(self._send, line)

    def _send(self, line):
        """
        Sends a raw IRC line unchecked. Doesn't do connected check, and is *not* threadsafe
        :type line: str
        """
        logger.info("[{}] >> {}".format(self.name, line))
        asyncio.async(self._protocol.send(line), loop=self.loop)


    @property
    def connected(self):
        return self._connected


class _IrcProtocol(asyncio.Protocol):
    """
    :type loop: asyncio.events.AbstractEventLoop
    :type conn: IrcClient
    :type bot: cloudbot.bot.CloudBot
    :type _input_buffer: bytes
    :type _connected: bool
    :type _transport: asyncio.transports.Transport
    :type _connected_future: asyncio.Future
    """

    def __init__(self, conn):
        """
        :type conn: IrcClient
        """
        self.loop = conn.loop
        self.bot = conn.bot
        self.conn = conn

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
        self._connected_future = asyncio.Future(loop=self.loop)
        if exc is None:
            # we've been closed intentionally, so don't reconnect
            return
        logger.error("[{}] Connection lost: {}".format(self.conn.name, exc))
        asyncio.async(self.conn.connect(), loop=self.loop)

    def eof_received(self):
        self._connected = False
        # create a new connected_future for when we are connected.
        self._connected_future = asyncio.Future(loop=self.loop)
        logger.info("[{}] EOF received.".format(self.conn.name))
        asyncio.async(self.conn.connect(), loop=self.loop)
        return True

    @asyncio.coroutine
    def send(self, line):
        # make sure we are connected before sending
        if not self._connected:
            yield from self._connected_future
        line = line[:510] + "\r\n"
        data = line.encode("utf-8", "replace")
        self._transport.write(data)

    def data_received(self, data):
        self._input_buffer += data

        while b"\r\n" in self._input_buffer:
            line_data, self._input_buffer = self._input_buffer.split(b"\r\n", 1)
            line = decode(line_data)

            # parse the line into a message
            if line.startswith(":"):
                prefix_line_match = irc_prefix_re.match(line)
                if prefix_line_match is None:
                    logger.critical("[{}] Received invalid IRC line '{}' from {}".format(
                        self.conn.name, line, self.conn.describe_server()))
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
                        self.conn.name, line, self.conn.describe_server()))
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
            event = Event(bot=self.bot, conn=self.conn, event_type=event_type, content=content, target=target,
                          channel=channel, nick=nick, user=user, host=host, mask=mask, irc_raw=line, irc_prefix=prefix,
                          irc_command=command, irc_paramlist=command_params, irc_ctcp_text=ctcp_text)

            # handle the message, async
            asyncio.async(self.bot.process(event), loop=self.loop)
