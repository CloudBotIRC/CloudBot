from util import hook

ignorelist = []


def ignore_target(target):
    """ ignores someone """
    target = target.lower()
    ignorelist.append(target)


def unignore_target(target):
    """ unignores someone """
    target = target.lower()
    ignorelist.remove(target)


def is_ignored(target):
    """ checks of someone is ignored """
    target = target.lower()
    if target in ignorelist:
        return True
    else:
        return False


@hook.sieve
def ignoresieve(bot, input, func, type, args):
    """ blocks input from ignored channels/users """
    # don't block input to event hooks
    if type == "event":
        return input
    if is_ignored(input.chan) or is_ignored(input.nick):
        if input.command == "PRIVMSG" and input.lastparam[1:] == "unignore":
            return input
        else:
            return None
    return input


@hook.command(autohelp=False)
def ignored(inp, bot=None):
    ".ignored -- Lists ignored channels/users."
    if ignorelist:
        return "Ignored channels/users are: %s" % ", ".join(ignorelist)
    else:
        return "No channels/users are currently ignored."


@hook.command(adminonly=True)
def ignore(inp, input=None, notice=None):
    ".ignore <channel/user> -- Makes the bot ignore <channel/user>."
    target = inp

    if is_ignored(target):
        notice("%s is already ignored." % target)
    else:
        ignore_target(target)
        notice("%s has been ignored." % target)


@hook.command(adminonly=True)
def unignore(inp, input=None, notice=None):
    ".unignore <channel/user> -- Makes the bot listen to <channel/user>."
    target = inp

    if is_ignored(target):
        unignore_target(target)
        notice("%s has been unignored." % target)
        return
    else:
        notice("%s is not ignored." % target)
        return
