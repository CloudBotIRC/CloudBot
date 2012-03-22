# mute plugin by lukeroge and neersighted
from util import hook

muted = []


def mute_target(target):
    target = target.lower()
    muted.append(target)


def unmute_target(target):
    target = target.lower()
    muted.remove(target)


def is_muted(target):
    target = target.lower()
    if target in muted:
        return True
    else:
        return False


@hook.sieve
def mutesieve(bot, input, func, type, args):
    if type == "event":
       return input
    if is_muted(input.chan) or is_muted(input.nick):
        if input.command == "PRIVMSG" and input.lastparam[1:] == "unmute":
            return input
        else:
            return None
    return input


@hook.command(autohelp=False)
def listmuted(inp, bot=None):
    ".listmuted -- Lists muted users/channels."
    if muted:
        return "Muted users/channels are: " + ", ".join(muted)
    else:
        return "No users are currently muted."


@hook.command(adminonly=True)
def mute(inp, input=None, db=None):
    ".mute <channel/user> -- Makes the bot ignore <channel/user>."
    "If no channel is specified, it is muted in the current channel."
    target = inp

    if is_muted(target):
        input.notice("%s is already muted." % target)
    else:
        mute_target(target)
        input.notice("%s has been muted." % target)


@hook.command(adminonly=True)
def unmute(inp, input=None, db=None):
    ".unmute <channel/user> -- Makes the bot listen to <channel/user>."
    "If no channel is specified, it is unmuted in the current channel."
    target = inp
    
    if is_muted(target):
        unmute_target(target)
        input.notice("%s has been unmuted." % target)
        return
    else:
        input.notice("%s is not muted." % target)
        return
