import asyncio
from collections import deque
import datetime
import logging

from cloudbot.permissions import PermissionManager

logger = logging.getLogger("cloudbot")


class Client:
    """
    A Client representing each connection the bot makes to a single server
    :type bot: cloudbot.bot.CloudBot
    :type loop: asyncio.events.AbstractEventLoop
    :type name: str
    :type readable_name: str
    :type channels: list[str]
    :type config: dict[str, unknown]
    :type nick: str
    :type vars: dict
    :type history: dict[str, list[tuple]]
    :type permissions: PermissionManager
    """

    def __init__(self, bot, name, nick, *, readable_name, channels=None, config=None):
        """
        :type bot: cloudbot.bot.CloudBot
        :type name: str
        :type readable_name: str
        :type nick: str
        :type channels: list[str]
        :type config: dict[str, unknown]
        """
        self.bot = bot
        self.loop = bot.loop
        self.name = name
        self.nick = nick
        self.readable_name = readable_name

        if channels is None:
            self.channels = []
        else:
            self.channels = channels

        if config is None:
            self.config = {}
        else:
            self.config = config
        self.vars = {}
        self.history = {}

        # create permissions manager
        self.permissions = PermissionManager(self)

    def describe_server(self):
        raise NotImplementedError

    @asyncio.coroutine
    def connect(self):
        """
        Connects to the server, or reconnects if already connected.
        """
        raise NotImplementedError

    def quit(self, reason=None):
        """
        Gracefully disconnects from the server with reason <reason>, close() should be called shortly after.
        """
        raise NotImplementedError

    def close(self):
        """
        Disconnects from the server, only for use when this Client object will *not* ever be connected again
        """
        raise NotImplementedError

    def message(self, target, *text):
        """
        Sends a message to the given target
        :type target: str
        :type text: tuple[str]
        """
        raise NotImplementedError

    def action(self, target, text):
        """
        Sends an action (or /me) to the given target channel
        :type target: str
        :type text: str
        """
        raise NotImplementedError

    def notice(self, target, text):
        """
        Sends a notice to the given target
        :type target: str
        :type text: str
        """
        raise NotImplementedError

    def set_nick(self, nick):
        """
        Sets the bot's nickname
        :type nick: str
        """
        raise NotImplementedError

    def join(self, channel):
        """
        Joins a given channel
        :type channel: str
        """
        raise NotImplementedError

    def part(self, channel):
        """
        Parts a given channel
        :type channel: str
        """
        raise NotImplementedError

    @property
    def connected(self):
        raise NotImplementedError


# TODO: Tracking of user 'mode' in channels
class User:
    """
    :param nick: The nickname of this User
    :param ident: The IRC ident of this User, if applicable
    :param host: The hostname of this User, if applicable
    :param mask: The IRC mask (nick!ident@host), if applicable
    :param mode: The IRC mode, if applicable
    :type nick: str
    :type ident: str
    :type host: str
    :type mask: str
    :type mask_known: bool
    :type mode: str
    """

    def __init__(self, nick, *, ident=None, host=None, mask=None, mode=''):
        self.nick = nick
        self.ident = ident
        self.host = host
        self.mask = mask
        self.mask_known = mask is not None
        self.mode = mode


class Channel:
    """
    name: the name of this channel
    users: A dict from nickname to User in this channel
    user_modes: A dict from User to an str containing all of the user's modes in this channel
    history: A list of (User, timestamp, message content)
    :type name: str
    :type users: dict[str, User]
    :type user_modes: dict[User, str]
    :type history: deque[(User, datetime, str)]

    """

    def __init__(self, name):
        self.name = name
        self.users = {}
        self.user_modes = {}
        self.history = deque(maxlen=100)
        self.topic = ""

    def track_message(self, event):
        """
        Adds a message to this channel's history, adding user info from the message as well
        :type event: cloudbot.event.Event
        """
        user = self.users[event.nick.lower()]
        if not user.mask_known:
            user.ident = event.user
            user.host = event.host
            user.mask = event.mask

        self.history.append((user, datetime.datetime.now(), event.content))

    def track_join(self, event):
        """
        :type event: cloudbot.event.Event
        """
        self.users[event.nick.lower()] = User(event.nick, ident=event.user, host=event.host, mask=event.mask, mode='')

    def track_part(self, event):
        """
        :type event: cloudbot.event.Event
        """
        del self.users[event.nick.lower()]

    def track_topic(self, event):
        """
        :type event: cloudbot.event.Event
        """
        self.topic = event.content

    def track_mode_change(self, event):
        """
        :type event: cloudbot.event.Event
        """
        user = self.users[event.nick.lower()]
        pass