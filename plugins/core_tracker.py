# plugin to keep track of bot state

import asyncio
import logging
import re

from cloudbot import hook

logger = logging.getLogger("cloudbot")

nick_re = re.compile(":(.+?)!")


@asyncio.coroutine
@hook.irc_raw("KICK")
def on_kick(conn, chan, nick):
    """
    :type conn: cloudbot.client.Client
    :type chan: str
    :type nick: str
    """
    # if the bot has been kicked, remove from the channel list
    if nick == conn.nick:
        if chan in conn.channels:
            conn.channels.remove(chan)
        if conn.config.get('auto_rejoin', False):
            conn.join(chan)


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
    if old_nick == conn.nick:
        conn.nick = new_nick
        logger.info("Bot nick changed from '{}' to '{}'.".format(old_nick, new_nick))


# for channels the host tells us we're joining without us joining it ourselves
# mostly when using a BNC which saves channels
@asyncio.coroutine
@hook.irc_raw("JOIN")
def on_join(conn, chan, nick):
    """
    :type conn: cloudbot.client.Client
    :type chan: str
    :type nick: str
    """
    if nick == conn.nick:
        if chan not in conn.channels:
            conn.channels.append(chan)
