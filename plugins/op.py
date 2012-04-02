# Plugin made by iloveportalz0r, TheNoodle, Lukeroge and neersighted
from util import hook

@hook.command(adminonly=True)
def kick(inp, chan=None, conn=None, notice=None):
    ".kick [channel] <user> [reason] -- Makes the bot kick <user> in [channel] "\
    "If [channel] is blank the bot will kick the <user> in "\
    "the channel the command was used in."
    split = inp.split(" ")
    if split[0][0] == "#":
        chan = split[0]
        user = split[1]
        out = "KICK %s %s" % (chan, user)
        if len(split) > 2:
            reason = ""
            for x in split[2:]:
                reason = reason + x + " "
            reason = reason[:-1]
            out = out + " :" + reason
    else:
        user = split[0]
        out = "KICK %s %s" % (chan, split[0])
        if len(split) > 1:
            reason = ""
            for x in split[1:]:
                reason = reason + x + " "
            reason = reason[:-1]
            out = out + " :" + reason

    notice("Attempting to kick %s from %s..." % (user, chan))
    conn.send(out)

@hook.command(adminonly=True)
def topic(inp, conn=None, chan=None, notice=None):
    ".topic [channel] <topic> -- Change the topic of a channel."
    split = inp.split(" ")
    if split[0][0] == "#":
        out = "PRIVMSG %s :%s" % (split[0], message)
    else:
        out = "TOPIC %s :%s" % (chan, message)
    conn.send(out)
