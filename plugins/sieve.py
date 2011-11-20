import re

from util import hook


@hook.sieve
def sieve_suite(bot, input, func, kind, args):
    if input.command == 'PRIVMSG' and \
       input.nick.lower()[-3:] == 'bot' and args.get('ignorebots', True):
            return None

    if kind == "command":
        if input.trigger in bot.config.get('disabled_commands', []):
            return None

        ignored = bot.config.get('ignored', [])
        if input.host in ignored or input.nick in ignored:
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

    if args.get('adminonly', False):
        admins = bot.config.get('admins', [])

        if input.host not in admins and input.nick not in admins:
            return None

    return input
