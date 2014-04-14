from util import hook, bucket

TOKENS = 10
RESTORE_RATE = 2
MESSAGE_COST = 5

buckets = {}


@hook.sieve
def sieve_suite(bot, input, func, kind, args):
    """
    :type bot: core.bot.CloudBot
    :type input: core.main.Input
    :type kind: str
    :type args: dict[str, unknown]
    """
    conn = input.conn
    # check ignorebots
    if input.command == 'PRIVMSG' and \
            input.nick.endswith('bot') and args.get('ignorebots', True):
        return None

    # check acls
    acl = conn.config.get('acls', {}).get(func.__name__)
    if acl:
        if 'deny-except' in acl:
            allowed_channels = list(map(str.lower, acl['deny-except']))
            if input.chan.lower() not in allowed_channels:
                return None
        if 'allow-except' in acl:
            denied_channels = list(map(str.lower, acl['allow-except']))
            if input.chan.lower() in denied_channels:
                return None

    # check disabled_commands
    if kind == "command":
        disabled_commands = conn.config.get('disabled_commands', [])
        if input.trigger in disabled_commands:
            return None

    # check permissions
    if args.get('adminonly', False):
        args["permissions"] = ["adminonly"]
    if args.get('permissions', False):
        allowed_permissions = args.get('permissions', [])
        allowed = False
        for perm in allowed_permissions:
            if input.has_permission(perm):
                allowed = True
                break

        if not allowed:
            input.notice("Sorry, you are not allowed to use this command.")
            return None

    # check command spam tokens
    if kind == "command":
        uid = input.chan

        if not uid in buckets:
            _bucket = bucket.TokenBucket(TOKENS, RESTORE_RATE)
            _bucket.consume(MESSAGE_COST)
            buckets[uid] = _bucket
            return input

        _bucket = buckets[uid]
        if _bucket.consume(MESSAGE_COST):
            pass
        else:
            print("pong!")
            return None

    return input
