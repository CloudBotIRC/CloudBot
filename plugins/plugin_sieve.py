import asyncio

from cloudbot import hook
from cloudbot.plugin import HookType
from cloudbot.util import bucket

plugin_info = {
    "plugin_category": "core"
}

command_limiting_initial_tokens = 10
command_limiting_restore_rate = 1
command_limiting_message_cost = 4

channel_buckets = {}


@asyncio.coroutine
@hook.sieve()
def sieve_suite(event):
    """
    :type event: cloudbot.event.Event
    """

    # check permissions
    allowed_permissions = event.hook.permissions
    if allowed_permissions:
        for perm in allowed_permissions:
            if event.has_permission(perm):
                break
        else:  # This executes when 'break' above doesn't
            event.notice("Sorry, you don't have access to this command.")
            return None

    # check command spam tokens
    if event.hook.type is HookType.command:
        if not event.chan_name in channel_buckets:
            _bucket = bucket.TokenBucket(command_limiting_initial_tokens, command_limiting_restore_rate)
            channel_buckets[event.chan_name] = _bucket
        else:
            _bucket = channel_buckets[event.chan_name]

        if not _bucket.consume(command_limiting_message_cost):
            event.notice("Command rate-limited, please try again in a few seconds.")
            return None

    return event
