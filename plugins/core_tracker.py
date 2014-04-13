# plugin to keep track of bot state

import re

from util import hook


nick_re = re.compile(":(.+?)!")


@hook.event("KICK")
def on_kick(paramlist, conn=None, chan=None):
    """
    :type paramlist: list[str]
    :type conn: core.irc.BotConnection
    :type chan: str
    """
    # if the bot has been kicked, remove from the channel list
    if paramlist[1] == conn.nick:
        conn.channels.remove(chan)
        auto_rejoin = conn.config.get('auto_rejoin', False)
        if auto_rejoin:
            conn.join(paramlist[0])


@hook.event("NICK")
def on_nick(paramlist, bot=None, conn=None, raw=None):
    """
    :type paramlist: list[str]
    :type bot: core.bot.CloudBot
    :type conn: core.irc.BotConnection
    :type raw: str
    """
    old_nick = nick_re.search(raw).group(1)
    new_nick = str(paramlist[0])
    if old_nick == conn.nick:
        conn.nick = new_nick
        bot.logger.info("Bot nick changed from '{}' to '{}'.".format(old_nick, new_nick))
