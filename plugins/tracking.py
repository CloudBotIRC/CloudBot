# plugin to keep track of bot state

import asyncio
import logging
import re

from cloudbot import hook

logger = logging.getLogger('cloudbot')

nick_re = re.compile(":(.+?)!")


@asyncio.coroutine
@hook.irc_raw("NICK")
def on_nick(conn, irc_raw, content):
    """
    :type conn: cloudbot.connection.Connection
    :type irc_raw: str
    :type content: str
    """
    old_nick = nick_re.search(irc_raw).group(1)
    if old_nick == conn.bot_nick:
        conn.bot_nick = new_nick = content
        logger.info("Bot nick changed from '{}' to '{}'.".format(old_nick, new_nick))

