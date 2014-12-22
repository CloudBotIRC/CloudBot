import asyncio

from cloudbot import hook
from cloudbot.plugin import HookType
from cloudbot.util import bucket

TOKENS = 10
RESTORE_RATE = 1
MESSAGE_COST = 4

channel_buckets = {}


@asyncio.coroutine
@hook.sieve
def sieve_suite(event):
    """
    :type event: cloudbot.event.Event
    """

    # check permissions
    allowed_permissions = event.hook.permissions
    if allowed_permissions:
        allowed = False
        for perm in allowed_permissions:
            if event.has_permission(perm):
                allowed = True
                break

        if not allowed:
            event.notice("Sorry, you are not allowed to use this command.")
            return None

    # check command spam tokens
    if event.hook.type is HookType.command:
        if not event.chan in channel_buckets:
            _bucket = bucket.TokenBucket(TOKENS, RESTORE_RATE)
            _bucket.consume(MESSAGE_COST)
            channel_buckets[event.chan] = _bucket
            return event

        _bucket = channel_buckets[event.chan]
        if not _bucket.consume(MESSAGE_COST):
            event.notice("Command rate-limited, please try again in a few seconds.")
            return None

    return event
