import re

from util import hook
from fnmatch import fnmatch


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
        allowed_groups = []

        # loop over every group
        for key, value in groups.iteritems():
            # loop over every permission the command allows
            for permission in allowed_permissions:
                # see if the group has that permission
                print value
                if permission in value["perms"]:
                    # if so, add the group name to the allowed_groups list
                    allowed_groups.append(key)

        if not allowed_groups:
            print "Something is wrong. A hook requires {} but" \
                  " there are no groups with that permission!".format(str(allowed_permissions))

        mask = input.mask.lower()

        for group in allowed_groups:
            group_users = bot.config.get("permissions", {}).get(group, [])["users"]
            group_users = [_mask.lower() for _mask in group_users]
            for pattern in group_users:
                if fnmatch(mask, pattern):
                    return input

        input.notice("Sorry, you are not allowed to use this command.")
        return None

    return input
