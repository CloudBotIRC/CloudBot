import re
from fnmatch import fnmatch

from util import hook


@hook.sieve
def sieve_suite(bot, input, func, kind, args):
    if input.command == 'PRIVMSG' and \
            input.nick.endswith('bot') and args.get('ignorebots', True):
        return None

    if kind == "command":
        if input.trigger in bot.config.get('disabled_commands', []):
            return None

    fn = re.match(r'^plugins.(.+).py$', func._filename)
    disabled = bot.config.get('disabled_plugins', [])
    if fn and fn.group(1).lower() in disabled:
        return None

    acl = bot.config.get('acls', {}).get(func.__name__)
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
        groups = bot.config.get("permissions", [])

        allowed_permissions = args.get('permissions', [])

        mask = input.mask.lower()

        # loop over every group
        for key, group in groups.iteritems():
            # loop over every permission the command allows
            for permission in allowed_permissions:
                # see if the group has that permission
                if permission in group["perms"]:
                    # if so, check it
                    group_users = [_mask.lower() for _mask in group["users"]]
                    for pattern in group_users:
                        if fnmatch(mask, pattern):
                            print "Allowed group {}.".format(group)
                            return input

        input.notice("Sorry, you are not allowed to use this command.")
        return None

    return input
