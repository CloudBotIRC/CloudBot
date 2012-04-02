import json
from util import hook

@hook.sieve
def ignoresieve(bot, input, func, type, args):
    """ blocks input from ignored channels/nicks """
    ignorelist = bot.config["plugins"]["ignore"]["ignored"]
    # don't block input to event hooks
    if type == "event":
        return input
    if input.chan in ignorelist or input.nick in ignorelist or input.host in ignorelist or input.mask in ignorelist:
        if input.command == "PRIVMSG" and input.lastparam[1:] == "unignore":
            return input
        else:
            return None
    return input


@hook.command(autohelp=False)
def ignored(inp, notice=None, bot=None):
    ".ignored -- Lists ignored channels/nicks/hosts."
    ignorelist = bot.config["plugins"]["ignore"]["ignored"]
    if ignorelist:
        notice("Ignored channels/nicks/hosts are: %s" % ", ".join(ignorelist))
    else:
        notice("No channels/nicks/hosts are currently ignored.")
    return


@hook.command(adminonly=True)
def ignore(inp, notice=None, bot=None, config=None):
    ".ignore <channel|nick|host> -- Makes the bot ignore <channel|nick|host>."
    target = inp.lower()
    ignorelist = bot.config["plugins"]["ignore"]["ignored"]
    if target in ignorelist:
        notice("%s is already ignored." % target)
    else:
        notice("%s has been ignored." % target)
        ignorelist.append(target)
        ignorelist.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    return

@hook.command(adminonly=True)
def unignore(inp, notice=None, bot=None, config=None):
    ".unignore <channel|nick|host> -- Makes the bot listen to <channel|nick|host>."
    target = inp.lower()
    ignorelist = bot.config["plugins"]["ignore"]["ignored"]
    if target in ignorelist:
        notice("%s has been unignored." % target)
        ignorelist.remove(target)
        ignorelist.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    else:
        notice("%s is not ignored." % target)
    return

