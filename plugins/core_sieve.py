import asyncio

from cloudbot import hook
from cloudbot.util import bucket

TOKENS = 10
RESTORE_RATE = 2
MESSAGE_COST = 5

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
            _bucket = bucket.TokenBucket(TOKENS, RESTORE_RATE)
            _bucket.consume(MESSAGE_COST)
            buckets[uid] = _bucket
            return event

        _bucket = buckets[uid]
        if _bucket.consume(MESSAGE_COST):
            pass
        else:
            # bad person loses all tokens
            #_bucket.empty()
            bot.logger.info("[{}] Refused command from {}. Entity has {} tokens, needs {}.".format(conn.readable_name,
                                                                                                   uid,
                                                                                                   _bucket.tokens,
                                                                                                   MESSAGE_COST))
            return None

    return event
