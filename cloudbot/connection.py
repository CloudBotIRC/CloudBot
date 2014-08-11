import asyncio
from collections import deque
import datetime
import logging
import re

from cloudbot.event import EventType
from cloudbot.permissions import PermissionManager
from cloudbot.util.dictionaries import CaseInsensitiveDict

logger = logging.getLogger("cloudbot")

mode_re = re.compile(r'([@&~%\+]*)([a-zA-Z0-9_\\\[\]\{\}\^`\|][a-zA-Z0-9_\\\[\]\{\}\^`\|-]*)')
symbol_to_mode = {
    '+': 'v',
    '@': 'o',
    # TODO: more of these, for half-op and stuff
}


class Connection:
    """
    A Connection representing each connection the bot makes to a single server
    :type bot: cloudbot.bot.CloudBot
    :type loop: asyncio.events.AbstractEventLoop
    :type name: str
    :type readable_name: str
    :type channels: dict[str, Channel]
    :type config: dict[str, str | dict | list]
    :type bot_nick: str
    :type permissions: PermissionManager
    :type waiting_messages: list[(str, str, re.__Regex, asyncio.Future)]
    """

    def __init__(self, bot, name, bot_nick, *, readable_name, config):
        """
        :type bot: cloudbot.bot.CloudBot
        :type name: str
        :type readable_name: str
        :type bot_nick: str
        :type config: dict[str, unknown]
        """
        self.bot = bot
        self.loop = bot.loop
        self.name = name
        self.bot_nick = bot_nick
        self.readable_name = readable_name

        self.channels = CaseInsensitiveDict()

        self.config = config

        # create permissions manager
        self.permissions = PermissionManager(self)

        self.waiting_messages = []

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
        Disconnects from the server, only for use when this Connection object will *not* ever be connected again
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

    @asyncio.coroutine
    def wait_for(self, message, nick=None, chan=None):
        """
        Waits for a message matching a specific regex
        :type nick: str
        :type message: str | re.__Regex
        """
        if nick is not None:
            nick = nick.lower()
        if chan is not None:
            chan = chan.lower()
        future = asyncio.Future(loop=self.bot.loop)
        if not hasattr(message, "search"):
            message = re.compile(message)

        key = (nick, chan, message, future)

        self.waiting_messages.append(key)
        result = yield from future
        self.waiting_messages.remove(key)
        return result

    @asyncio.coroutine
    def pre_process_event(self, event):

        if event.type is EventType.nick and event.nick.lower() == self.bot_nick.lower():
            logger.info("[{}] Bot nick changed from {} to {}.".format(self.readable_name, self.bot_nick, event.content))
            self.bot_nick = event.content

        if event.chan_name is None or event.chan_name.lower() == event.nick.lower():
            return  # the rest of this just process on channels
        channel = self.channels.get(event.chan_name)
        if channel is None:
            if event.type is not EventType.join:
                logger.warning("First mention of channel {} was from event type {}".format(event.chan_name, event.type))
            elif event.type is EventType.part and event.nick.lower() == self.bot_nick.lower():
                return  # no need to create a channel when we're just leaving it
            elif event.nick.lower() != self.bot_nick.lower():
                logger.warning("First join of channel {} was {}".format(event.chan_name, event.nick))
            channel = Channel(event.chan_name)
            self.channels[event.chan_name] = channel

        event.channel = channel

        if event.type is EventType.part:
            if event.nick.lower() == self.bot_nick.lower():
                del self.channels[event.chan_name]
                return
        elif event.type is EventType.kick:
            if event.target.lower() == self.bot_nick.lower():
                del self.channels[event.chan_name]
                return

        if event.type is EventType.message:
            channel.track_message(event)
        elif event.type is EventType.join:
            channel.track_join(event)
        elif event.type is EventType.part:
            channel.track_part(event)
        elif event.type is EventType.kick:
            channel.track_kick(event)
        elif event.type is EventType.topic:
            channel.track_topic(event)
        elif event.irc_command == 'MODE':
            channel.track_mode(event)
        elif event.irc_command == '353':
            channel.track_353_channel_list(event)


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
        self.users = CaseInsensitiveDict()
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

        self.history.append((EventType.message, user.nick, datetime.datetime.now(), event.content))

    def track_join(self, event):
        """
        :type event: cloudbot.event.Event
        """
        self.users[event.nick] = User(event.nick, ident=event.user, host=event.host, mask=event.mask, mode='')
        self.history.append((EventType.join, event.nick, datetime.datetime.now(), None))

    def track_part(self, event):
        """
        :type event: cloudbot.event.Event
        """
        del self.users[event.nick]
        self.history.append((EventType.part, event.nick, datetime.datetime.now(), event.content))

    def track_kick(self, event):
        """
        :type event: cloudbot.event.Event
        """
        del self.users[event.target]
        # TODO: Better way of storing both kicker and target in history
        self.history.append((EventType.kick, event.nick, datetime.datetime.now(), (event.target, event.content)))

    def track_topic(self, event):
        """
        :type event: cloudbot.event.Event
        """
        self.topic = event.content
        self.history.append((EventType.topic, event.nick, datetime.datetime.now(), event.content))

    def track_mode(self, event):
        """
        IRC-specific tracking of mode changing
        :type event: cloudbot.event.Event
        """
        user = self.users[event.target]
        mode_change = event.irc_command_params[1]  # in `:Dabo!dabo@dabo.us MODE #obr +v obr`, `+v` is the second param
        if mode_change[0] == '-':
            user.mode = user.mode.replace(mode_change[1], '')  # remove the mode from the mode string
        elif mode_change[0] == '+':
            if mode_change[1] not in user.mode:
                user.mode += mode_change[1]  # add the mode to the mode string
        else:
            logger.warning("Invalid mode string '" + mode_change + "' found, ignoring.")

    def track_353_channel_list(self, event):
        for user in event.content.split():
            match = mode_re.match(user)
            if match is None:
                logger.warning("User mode {} didn't fit specifications.".format(user))
            # find mode
            mode_symbols = match.group(1)
            mode = ''
            if mode_symbols is not None:
                for symbol in mode_symbols:
                    symbol_mode = symbol_to_mode.get(symbol)
                    if symbol_mode is not None:
                        mode += symbol_mode
            # create user
            nick = match.group(2)
            user = User(nick, mode=mode)
            self.users[nick] = user