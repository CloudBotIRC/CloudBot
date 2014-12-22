import asyncio
from fnmatch import fnmatch

from cloudbot import hook
from cloudbot.plugin import HookType


@asyncio.coroutine
@hook.sieve()
def ignore_sieve(event):
    """ blocks events from ignored channels/hosts
    :type event: cloudbot.event.Event
    """
    bot = event.bot
    # don't block event hooks
    if event.hook.type is HookType.event or event.hook.type is HookType.irc_raw:
        return event

    # don't block server messages
    if event.mask is None:
        return event

    # don't block an event that could be unignoring
    if event.hook.type is HookType.command and event.hook.function_name == 'unignore':
        return event

    ignore_list = yield from event.async(bot.db.smembers, "plugins:ignore:ignored")

    mask = event.mask.lower()
    for pattern in ignore_list:
        pattern = pattern.decode()
        if (pattern.startswith('#') and fnmatch(pattern, event.chan)) or fnmatch(mask, pattern):
            return None

    return event


@asyncio.coroutine
@hook.command(autohelp=False, permissions=["ignored.view"])
def ignored(notice, async, db):
    """- lists all channels and users I'm ignoring"""

    ignore_list = yield from async(db.smembers, 'plugins:ignore:ignored')
    if ignore_list:
        notice("Ignored users: {}".format(", ".join(b.decode() for b in ignore_list)))
    else:
        notice("No users are currently ignored.")
    return


@asyncio.coroutine
@hook.command(permissions=['ignored.manage'])
def ignore(text, async, db):
    """<nick|usermask> - adds <channel|nick> to my ignore list
    :type db: redis.StrictRedis
    """
    target = text.lower()
    if ('!' not in target or '@' not in target) and not target.startswith('#'):
        target = '{}!*@*'.format(target)

    added = yield from async(db.sadd, 'plugins:ignore:ignored', target)

    if added > 0:
        return "{} has been ignored.".format(target)
    else:
        return "{} is already ignored.".format(target)


@asyncio.coroutine
@hook.command(permissions=['ignored.manage'])
def unignore(text, async, db):
    """<nick|usermask> - removes <nick|usermask> from my ignore list
    :type db: redis.StrictRedis
    """
    target = text.lower()
    if ('!' not in target or '@' not in target) and not target.startswith('#'):
        target = '{}!*@*'.format(target)

    removed = yield from async(db.srem, 'plugins:ignore:ignored', target)

    if removed > 0:
        return "{} has been unignored.".format(target)
    else:
        return "{} was not ignored.".format(target)
