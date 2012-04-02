# Plugin made by Lukeroge and neersighted
from util import hook


@hook.command(adminonly=True)
def topic(inp, conn=None, chan=None, notice=None):
    ".topic [channel] <topic> -- Change the topic of a channel."
    inp = inp.split(" ")
    if inp[0][0] == "#":
        out = "PRIVMSG %s :%s" % (inp[0], message)
    else:
        out = "TOPIC %s :%s" % (chan, message)
    conn.send(out)


@hook.command(adminonly=True)
def kick(inp, chan=None, conn=None, notice=None):
    ".kick [channel] <user> [reason] -- Makes the bot kick <user> in [channel] "\
    "If [channel] is blank the bot will kick the <user> in "\
    "the channel the command was used in."
    inp = inp.split(" ")
    if inp[0][0] == "#":
        chan = inp[0]
        user = inp[1]
        out = "KICK %s %s" % (chan, user)
        if len(inp) > 2:
            reason = ""
            for x in inp[2:]:
                reason = reason + x + " "
            reason = reason[:-1]
            out = out + " :" + reason
    else:
        user = inp[0]
        out = "KICK %s %s" % (chan, user)
        if len(inp) > 1:
            reason = ""
            for x in inp[1:]:
                reason = reason + x + " "
            reason = reason[:-1]
            out = out + " :" + reason

    notice("Attempting to kick %s from %s..." % (user, chan))
    conn.send(out)


@hook.command(adminonly=True)
def ban(inp, conn=None, chan=None, notice=None):
    ".ban [channel] <user> -- Makes the bot ban <user> in [channel]. "\
    "If [channel] is blank the bot will ban <user> in "\
    "the channel the command was used in."
    inp = inp.split(" ")
    if inp[0][0] == "#":
        chan = inp[0]
        user = inp[1]
        out = "MODE %s +b %s" % (chan, user)
    else:
        user = inp[0]
        out = "MODE %s +b %s" % (chan, user)
    notice("Attempting to ban %s from %s..." % (user, chan))
    conn.send(out)


@hook.command(adminonly=True)
def unban(inp, conn=None, chan=None, notice=None):
    ".unban [channel] <user> -- Makes the bot unban <user> in [channel]. "\
    "If [channel] is blank the bot will unban <user> in "\
    "the channel the command was used in."
    inp = inp.split(" ")
    if inp[0][0] == "#":
        chan = inp[0]
        user = inp[1]
        out = "MODE %s -b %s" % (chan, user)
    else:
        user = inp[0]
        out = "MODE %s -b %s" % (chan, user)
    notice("Attempting to unban %s from %s..." % (user, chan))
    conn.send(out)


@hook.command(adminonly=True)
def kickban(inp, chan=None, conn=None, notice=None):
    ".kickban [channel] <user> [reason] -- Makes the bot kickban <user> in [channel] "\
    "If [channel] is blank the bot will kickban the <user> in "\
    "the channel the command was used in."
    inp = inp.split(" ")
    if inp[0][0] == "#":
        chan = inp[0]
        user = inp[1]
        out1 = "MODE %s +b %s" % (chan, user)
        out2 = "KICK %s %s" % (chan, user)
        if len(inp) > 2:
            reason = ""
            for x in inp[2:]:
                reason = reason + x + " "
            reason = reason[:-1]
            out = out + " :" + reason
    else:
        user = inp[0]
        out1 = "MODE %s +b %s" % (chan, user)
        out2 = "KICK %s %s" % (chan, user)
        if len(inp) > 1:
            reason = ""
            for x in inp[1:]:
                reason = reason + x + " "
            reason = reason[:-1]
            out = out + " :" + reason

    notice("Attempting to kickban %s from %s..." % (user, chan))
    conn.send(out1)
    conn.send(out2)
