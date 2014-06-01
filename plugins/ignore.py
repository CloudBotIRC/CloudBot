import asyncio
from fnmatch import fnmatch

from cloudbot import hook


@hook.onload
def ensure_ignored(bot):
    changed = False
    for conn_config in bot.config["connections"]:
        if not "plugins" in conn_config:
            conn_config["plugins"] = {"ignore": {"ignored": []}}
            changed = True
        elif not "ignore" in conn_config["plugins"]:
            conn_config["plugins"]["ignore"] = {"ignored": []}
            changed = True
        elif not "ignored" in conn_config["plugins"]["ignore"]:
            conn_config["plugins"]["ignore"]["ignored"] = []
            changed = True

    if changed:
        bot.config.save_config()


@asyncio.coroutine
@hook.sieve()
def ignore_sieve(bot, event, _hook):
    """ blocks events from ignored channels/hosts
    :type bot: cloudbot.core.bot.CloudBot
    :type event: cloudbot.core.events.BaseEvent
    :type _hook: cloudbot.core.pluginmanager.Hook
    """
    # don't block event hooks
    if _hook.type == "event":
        return event

    # don't block an event that could be unignoring
    if event.irc_command == "PRIVMSG" and event.irc_message[1:] == "unignore":
        return event

    if event.mask is None:
        # this is a server message, we don't need to check it
        return event

    ignorelist = event.conn.config["plugins"]["ignore"]["ignored"]
    mask = event.mask.lower()

    for pattern in ignorelist:
        if (pattern.startswith("#") and fnmatch(pattern, event.chan)) or fnmatch(mask, pattern):
            return None

    return event


@asyncio.coroutine
@hook.command(autohelp=False)
def ignored(notice, conn):
    """- lists all channels and users I'm ignoring"""
    ignorelist = conn.config["plugins"]["ignore"]["ignored"]
    if ignorelist:
        notice("Ignored channels/users are: {}".format(", ".join(ignorelist)))
    else:
        notice("No masks are currently ignored.")
    return


@hook.command(permissions=["ignore"])
def ignore(text, bot, conn, notice):
    """<channel|nick|usermask> - adds <channel|nick> to my ignore list"""
    target = text.lower()
    if "!" not in target or "@" not in target:
        target = "{}!*@*".format(target)
    ignorelist = conn.config["plugins"]["ignore"]["ignored"]
    if target in ignorelist:
        notice("{} is already ignored.".format(target))
    else:
        notice("{} has been ignored.".format(target))
        ignorelist.append(target)
        ignorelist.sort()
        bot.config.save_config()
    return


@hook.command(permissions=["ignore"])
def unignore(text, bot, conn, notice):
    """<channel|nick|usermask> - removes <channel|nick|usermask> from my ignore list"""
    target = text.lower()
    if "!" not in target or "@" not in target:
        target = "{}!*@*".format(target)
    ignorelist = conn.config["plugins"]["ignore"]["ignored"]
    if target in ignorelist:
        notice("{} has been unignored.".format(target))
        ignorelist.remove(target)
        ignorelist.sort()
        bot.config.save_config()
    else:
        notice("{} is not ignored.".format(target))
    return
