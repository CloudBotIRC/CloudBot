"""
from util import hook

@hook.sieve
def mutesieve(bot, input, func, kind, args):
    if kind == "event":
        return input
    if input.chan <is_muted>:
        if input.command == "PRIVMSG" and input.lastparam[1:] == "unmute":
            return input
        else:
            return None
    return input

@hook.command
def mute(inp, input=None, db=None):
    ".mute <channel> -- Mutes the bot in <channel>. If no channel is specified, it is muted in the current channel."
    if inp:
        input.chan = inp
    if input.nick in input.bot.config["admins"]:
        <mute_bot>
        input.notice("Muted")
    else:
        input.notice("Only bot admins can use this command!")

@hook.command
def unmute(inp, input=None, db=None):
    ".unmute <channel> -- Unmutes the bot in <channel>. If no channel is specified, it is unmuted in the current channel."
    if inp:
        input.chan = inp
    if input.nick in input.bot.config["admins"]:
        if <ismuted>:
            input.notice("Already muted!")
        else:
           <mute_bot>
           input.notice("Muted")
    else:
        input.notice("Only bot admins can use this command!")
"""
