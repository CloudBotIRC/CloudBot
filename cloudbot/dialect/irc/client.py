from _ssl import PROTOCOL_SSLv23
import asyncio
import ssl
import logging
from ssl import SSLContext

from cloudbot.client import Client
from cloudbot.dialect.irc.protocol import IRCProtocol


logger = logging.getLogger("cloudbot")


class IRCClient(Client):
    """
    An implementation of Client for IRC.
    :type use_ssl: bool
    :type server: str
    :type port: int
    :type _connected: bool
    :type _ignore_cert_errors: bool
    """

    def __init__(self, bot, name, nick, *, readable_name, channels=None, config=None,
                 server, port=6667, use_ssl=False, ignore_cert_errors=True, timeout=300):
        """
        :type bot: cloudbot.core.bot.CloudBot
        :type name: str
        :type readable_name: str
        :type nick: str
        :type channels: list[str]
        :type config: dict[str, unknown]
        :type server: str
        :type port: int
        :type use_ssl: bool
        :type ignore_cert_errors: bool
        :type timeout: int
        """
        super().__init__(bot, name, nick, readable_name=readable_name, channels=channels, config=config)

        self.use_ssl = use_ssl
        self._ignore_cert_errors = ignore_cert_errors
        self._timeout = timeout
        self.server = server
        self.port = port

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
        # connect to the irc server
        if self._quit:
            # we've quit, so close instead (because this has probably been called because of EOF received)
            self.close()
            return

        if self._connected:
            logger.info("[{}] Reconnecting".format(self.readable_name))
            self._transport.close()
        else:
            self._connected = True
            logger.info("[{}] Connecting".format(self.readable_name))

        self._transport, self._protocol = yield from self.loop.create_connection(
            lambda: IRCProtocol(self), host=self.server, port=self.port, ssl=self.ssl_context)

        # send the password, nick, and user
        self.set_pass(self.config["connection"].get("password"))
        self.set_nick(self.nick)
        self.cmd("USER", self.config.get('user', 'cloudbot'), "3", "*",
                 self.config.get('realname', 'CloudBotRefresh - http://cloudbot.pw'))

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

    def message(self, target, text):
        self.cmd("PRIVMSG", target, text)

    def action(self, target, text):
        self.ctcp(target, "ACTION", text)

    def notice(self, target, text):
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
        logger.info("[{}] >> {}".format(self.readable_name, line))
        asyncio.async(self._protocol.send(line), loop=self.loop)

    @property
    def connected(self):
        return self._connected
