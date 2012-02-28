from util import hook
import usertracking
import time


@hook.sieve
def mutesieve(bot, input, func, kind, args):
    if kind == "event": 
        return input
    if "chan" in input.keys() and input.chan in input.conn.users.channels and hasattr(input.conn.users[input.chan], "mute"):
        if input.command == "PRIVMSG" and input.lastparam[1:] == "unmute":
            return input
        else:
            return None
    return input


@hook.command
def mute(inp, input=None, db=None, bot=None, users=None):
    if inp and inp in input.conn.users.channels.keys():
        input.chan = inp
    ".mute <channel> - Mutes the bot"
    if usertracking.query(db, bot.config, input.nick, input.chan, "mute") or "o" in users[input.chan].usermodes[input.nick]:
        users[input.chan].mute = "%s %d" % (input.nick, time.time())
        input.notice("Muted")
    else:
        input.notice("Only bot admins can use this command!")

@hook.command
def unmute(inp, input=None, db=None, bot=None, users=None):
    if inp and inp in users.channels.keys():
        input.chan = inp
    ".unmute <channel> - Unmutes the bot"
    if usertracking.query(db, bot.config, input.nick, input.chan, "mute") or "o" in users[input.chan].usermodes[input.nick]:
        if hasattr(users[input.chan], "mute"):
            input.notice("Unmuted")
            del users[input.chan].mute
        else:
            input.notice("Not Muted")
    else:
        input.notice("Only bot admins can use this command!")