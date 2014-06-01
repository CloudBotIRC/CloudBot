import asyncio
from cloudbot import bucket, hook

TOKENS = 10
RESTORE_RATE = 2
MESSAGE_COST = 5

buckets = {}


@asyncio.coroutine
@hook.sieve
def sieve_suite(bot, event, _hook):
    """
    :type bot: cloudbot.core.bot.CloudBot
    :type event: cloudbot.core.events.BaseEvent
    :type _hook: cloudbot.core.pluginmanager.Hook
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
        uid = event.chan

        if not uid in buckets:
            _bucket = bucket.TokenBucket(TOKENS, RESTORE_RATE)
            _bucket.consume(MESSAGE_COST)
            buckets[uid] = _bucket
            return event

        _bucket = buckets[uid]
        if _bucket.consume(MESSAGE_COST):
            pass
        else:
            print("pong!")
            return None

    return event
