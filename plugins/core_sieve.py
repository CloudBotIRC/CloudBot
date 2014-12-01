import asyncio

from time import time

from cloudbot import hook
from cloudbot.util.tokenbucket import TokenBucket

TOKENS = 17.5
RESTORE_RATE = 2.5
MESSAGE_COST = 5

# when STRICT is enabled, every time a user gets ratelimted it wipes
# their tokens so they have to wait at least X seconds to regen
STRICT = True

buckets = {}


@asyncio.coroutine
@hook.sieve
def sieve_suite(bot, event, _hook):
    """
    :type bot: cloudbot.bot.CloudBot
    :type event: cloudbot.event.Event
    :type _hook: cloudbot.plugin.Hook
    """
    conn = event.conn
    # check ignore bots
    if event.irc_command == 'PRIVMSG' and event.nick.endswith('bot') and _hook.ignore_bots:
        return None

    # check acls
    acl = conn.config.get('acls', {}).get(_hook.function_name)
    if acl:
        if 'deny-except' in acl:
            allowed_channels = list(map(str.lower, acl['deny-except']))
            if event.chan.lower() not in allowed_channels:
                return None
        if 'allow-except' in acl:
            denied_channels = list(map(str.lower, acl['allow-except']))
            if event.chan.lower() in denied_channels:
                return None

    # check disabled_commands
    if _hook.type == "command":
        disabled_commands = conn.config.get('disabled_commands', [])
        if event.triggered_command in disabled_commands:
            return None

    # check permissions
    allowed_permissions = _hook.permissions
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
    if _hook.type == "command":
        # right now ratelimiting is per-channel, but this can be changed
        uid = event.chan

        if uid not in buckets:
            bucket = TokenBucket(TOKENS, RESTORE_RATE)
            bucket.consume(MESSAGE_COST)
            buckets[uid] = bucket
            return event

        bucket = buckets[uid]
        if bucket.consume(MESSAGE_COST):
            pass
        else:
            if STRICT:
                # bad person loses all tokens
                bucket.empty()
            bot.logger.info("[{}] Refused command from {}. Entity has {} tokens, needs {}.".format(conn.readable_name,
                                                                                                   uid,
                                                                                                   bucket.tokens,
                                                                                                   MESSAGE_COST))
            return None

    return event

@hook.command
def clearbuckets():
    """temporary!"""

    # clear ratelimiting tokens that have not been accessed in
    # the last 10 minutes
    for uid, _bucket in buckets:
        if (time() - _bucket.timestamp) > 600:
            del buckets[uid]
