import json
from fnmatch import fnmatch

from util import hook


@hook.sieve
def ignore_sieve(bot, input, func, type, args):
    """ blocks input from ignored channels/hosts """
    ignorelist = bot.config["plugins"]["ignore"]["ignored"]
    mask = input.mask.lower()

    # don't block input to event hooks
    if type == "event":
        return input

    if ignorelist:
        for pattern in ignorelist:
            if pattern.startswith("#") and pattern in ignorelist:
                if input.command == "PRIVMSG" and input.lastparam[1:] == "unignore":
                    return input
                else:
                    return None
            elif fnmatch(mask, pattern):
                if input.command == "PRIVMSG" and input.lastparam[1:] == "unignore":
                    return input
                else:
                    return None

    return input


@hook.command(autohelp=False)
def ignored(inp, notice=None, bot=None):
    """ignored -- Lists ignored channels/users."""
    ignorelist = bot.config["plugins"]["ignore"]["ignored"]
    if ignorelist:
        notice("Ignored channels/users are: {}".format(", ".join(ignorelist)))
    else:
        notice("No masks are currently ignored.")
    return


@hook.command(permissions=["ignore"])
def ignore(inp, notice=None, bot=None, config=None):
    """ignore <channel|nick|host> -- Makes the bot ignore <channel|user>."""
    target = inp.lower()
    ignorelist = bot.config["plugins"]["ignore"]["ignored"]
    if target in ignorelist:
        notice("{} is already ignored.".format(target))
    else:
        notice("{} has been ignored.".format(target))
        ignorelist.append(target)
        ignorelist.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    return


@hook.command(permissions=["ignore"])
def unignore(inp, notice=None, bot=None, config=None):
    """unignore <channel|user> -- Makes the bot listen to
    <channel|user>."""
    target = inp.lower()
    ignorelist = bot.config["plugins"]["ignore"]["ignored"]
    if target in ignorelist:
        notice("{} has been unignored.".format(target))
        ignorelist.remove(target)
        ignorelist.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    else:
        notice("{} is not ignored.".format(target))
    return
