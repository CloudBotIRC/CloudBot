import asyncio
from fnmatch import fnmatch
import logging

from cloudbot import hook
from cloudbot.plugin import HookType

plugin_info = {
    "plugin_category": "core",
    "command_category_name": "Administration"
}

logger = logging.getLogger("cloudbot")


@asyncio.coroutine
@hook.sieve()
def ignore_sieve(event, hook_event):
    """ blocks events from ignored channels/hosts
    :type event: cloudbot.event.Event
    :type hook_event: cloudbot.event.HookEvent
    """
    bot = event.bot
    # don't block event hooks
    if hook_event.hook.type is HookType.event or hook_event.hook.type is HookType.irc_raw:
        return event

    # don't block server messages
    if event.mask is None:
        return event

    # don't block an event that could be un-ignoring
    if hook_event.hook.type is HookType.command and hook_event.hook.function_name == 'unignore':
        return event

    ignore_list = yield from event.async(bot.db.smembers, 'plugins:ignore:ignored')

    mask = event.mask.lower()
    for pattern in ignore_list:
        pattern = pattern.decode()
        if pattern.startswith('#'):
            if fnmatch(event.chan_name, pattern):
                logger.info("Ignoring {}: Skipping hook {}".format(event.chan_name, hook_event.hook.description))
                return None
        else:
            if fnmatch(mask, pattern):
                logger.info("Ignoring {}: Skipping hook {}".format(event.mask, hook_event.hook.description))
                return None

    return event


@asyncio.coroutine
@hook.command(autohelp=False, permissions=['ignored.view'])
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
    """<nick|user-mask> - adds <channel|nick> to my ignore list
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
    """<nick|user-mask> - removes <nick|user-mask> from my ignore list
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
