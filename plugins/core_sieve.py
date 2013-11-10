from util import hook, bucket

TOKENS = 10
RESTORE_RATE = 2
MESSAGE_COST = 5

buckets = {}

@hook.sieve
def sieve_suite(bot, input, func, kind, args):
    conn = input.conn
    if input.command == 'PRIVMSG' and \
            input.nick.endswith('bot') and args.get('ignorebots', True):
        return None

    if kind == "command":
        uid = (input.nick, input.chan)

        if not uid in buckets:
            _bucket = bucket.TokenBucket(TOKENS, RESTORE_RATE)
            _bucket.consume(MESSAGE_COST)
            buckets[uid] = _bucket
            return input

        _bucket = buckets[uid]
        if _bucket.consume(MESSAGE_COST):
            return input
        else:
            print "pong!"
            return None


        disabled_commands = conn.config.get('disabled_commands', [])
        if input.trigger in disabled_commands:
            return None


    acl = conn.config.get('acls', {}).get(func.__name__)
    if acl:
        if 'deny-except' in acl:
            allowed_channels = map(unicode.lower, acl['deny-except'])
            if input.chan.lower() not in allowed_channels:
                return None
        if 'allow-except' in acl:
            denied_channels = map(unicode.lower, acl['allow-except'])
            if input.chan.lower() in denied_channels:
                return None

    # shim so plugins using the old "adminonly" permissions format still work
    if args.get('adminonly', False):
        args["permissions"] = ["adminonly"]

    if args.get('permissions', False):
        mask = input.mask.lower()

        allowed_permissions = args.get('permissions', [])
        for perm in allowed_permissions:
            if conn.permissions.has_perm_legacy(mask, perm):
                return input

        input.notice("Sorry, you are not allowed to use this command.")
        return None

    return input
