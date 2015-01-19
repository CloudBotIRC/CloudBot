# plugin to keep track of bot state

import asyncio
import logging
import re
from collections import deque

from cloudbot import hook

logger = logging.getLogger("cloudbot")

nick_re = re.compile(":(.+?)!")


# functions called for bot state tracking

def bot_left_channel(conn, chan):
    logger.info("[{}|tracker] Bot left channel '{}'".format(conn.name, chan))
    if chan in conn.channels:
        conn.channels.remove(chan)
    if chan in conn.history:
        del conn.history[chan]


def bot_joined_channel(conn, chan):
    logger.info("[{}|tracker] Bot joined channel '{}'".format(conn.name, chan))
    conn.channels.append(chan)
    conn.history[chan] = deque(maxlen=100)


@asyncio.coroutine
@hook.irc_raw("KICK")
def on_kick(conn, chan, target, loop):
    """
    :type conn: cloudbot.client.Client
    :type chan: str
    :type nick: str
    """
    # if the bot has been kicked, remove from the channel list
    if target == conn.nick:
        bot_left_channel(conn, chan)
        if conn.config.get('auto_rejoin', False):
            loop.call_later(5, conn.join, chan)
            loop.call_later(5, logger.info, "[{}|tracker] Bot was kicked from {}, "
                                            "rejoining channel.".format(conn.name, chan))


@asyncio.coroutine
@hook.irc_raw("NICK")
def on_nick(irc_paramlist, conn, irc_raw):
    """
    :type irc_paramlist: list[str]
    :type conn: cloudbot.client.Client
    :type irc_raw: str
    """
    old_nick = nick_re.search(irc_raw).group(1)
    new_nick = str(irc_paramlist[0])

    # get rid of :
    if new_nick.startswith(":"):
        new_nick = new_nick[1:]

    if old_nick == conn.nick:
        conn.nick = new_nick
        logger.info("[{}|tracker] Bot nick changed from '{}' to '{}'.".format(conn.name, old_nick, new_nick))


# for channels the host tells us we're joining without us joining it ourselves
# mostly when using a BNC which saves channels
@asyncio.coroutine
@hook.irc_raw("JOIN")
def on_join(conn, chan, target):
    """
    :type conn: cloudbot.client.Client
    :type chan: str
    :type nick: str
    """
    if target == conn.nick:
        bot_joined_channel(conn, chan)


@asyncio.coroutine
@hook.irc_raw("PART")
def on_join(conn, chan, target):
    """
    :type conn: cloudbot.client.Client
    :type chan: str
    :type nick: str
    """
    if target == conn.nick:
        bot_joined_channel(conn, chan)
