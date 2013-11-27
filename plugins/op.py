from util import hook


def mode_cmd(mode, text, inp, chan, conn, notice):
    """ generic mode setting function """
    split = inp.split(" ")
    if split[0].startswith("#"):
        channel = split[0]
        target = split[1]
        notice("Attempting to {} {} in {}...".format(text, target, channel))
        conn.send("MODE {} {} {}".format(channel, mode, target))
    else:
        channel = chan
        target = split[0]
        notice("Attempting to {} {} in {}...".format(text, target, channel))
        conn.send("MODE {} {} {}".format(channel, mode, target))


def mode_cmd_no_target(mode, text, inp, chan, conn, notice):
    """ generic mode setting function without a target"""
    split = inp.split(" ")
    if split[0].startswith("#"):
        channel = split[0]
        notice("Attempting to {} {}...".format(text, channel))
        conn.send("MODE {} {}".format(channel, mode))
    else:
        channel = chan
        notice("Attempting to {} {}...".format(text, channel))
        conn.send("MODE {} {}".format(channel, mode))


@hook.command(permissions=["op_ban", "op"])
def ban(inp, conn=None, chan=None, notice=None):
    """ban [channel] <user> -- Makes the bot ban <user> in [channel].
    If [channel] is blank the bot will ban <user> in
    the channel the command was used in."""
    mode_cmd("+b", "ban", inp, chan, conn, notice)


@hook.command(permissions=["op_ban", "op"])
def unban(inp, conn=None, chan=None, notice=None):
    """unban [channel] <user> -- Makes the bot unban <user> in [channel].
    If [channel] is blank the bot will unban <user> in
    the channel the command was used in."""
    mode_cmd("-b", "unban", inp, chan, conn, notice)


@hook.command(permissions=["op_quiet", "op"])
def quiet(inp, conn=None, chan=None, notice=None):
    """quiet [channel] <user> -- Makes the bot quiet <user> in [channel].
    If [channel] is blank the bot will quiet <user> in
    the channel the command was used in."""
    mode_cmd("+q", "quiet", inp, chan, conn, notice)


@hook.command(permissions=["op_quiet", "op"])
def unquiet(inp, conn=None, chan=None, notice=None):
    """unquiet [channel] <user> -- Makes the bot unquiet <user> in [channel].
    If [channel] is blank the bot will unquiet <user> in
    the channel the command was used in."""
    mode_cmd("-q", "unquiet", inp, chan, conn, notice)


@hook.command(permissions=["op_voice", "op"])
def voice(inp, conn=None, chan=None, notice=None):
    """voice [channel] <user> -- Makes the bot voice <user> in [channel].
    If [channel] is blank the bot will voice <user> in
    the channel the command was used in."""
    mode_cmd("+v", "voice", inp, chan, conn, notice)


@hook.command(permissions=["op_voice", "op"])
def devoice(inp, conn=None, chan=None, notice=None):
    """devoice [channel] <user> -- Makes the bot devoice <user> in [channel].
    If [channel] is blank the bot will devoice <user> in
    the channel the command was used in."""
    mode_cmd("-v", "devoice", inp, chan, conn, notice)


@hook.command(permissions=["op_op", "op"])
def op(inp, conn=None, chan=None, notice=None):
    """op [channel] <user> -- Makes the bot op <user> in [channel].
    If [channel] is blank the bot will op <user> in
    the channel the command was used in."""
    mode_cmd("+o", "op", inp, chan, conn, notice)


@hook.command(permissions=["op_op", "op"])
def deop(inp, conn=None, chan=None, notice=None):
    """deop [channel] <user> -- Makes the bot deop <user> in [channel].
    If [channel] is blank the bot will deop <user> in
    the channel the command was used in."""
    mode_cmd("-o", "deop", inp, chan, conn, notice)


@hook.command(permissions=["op_topic", "op"])
def topic(inp, conn=None, chan=None):
    """topic [channel] <topic> -- Change the topic of a channel."""
    split = inp.split(" ")
    if split[0].startswith("#"):
        message = " ".join(split[1:])
        chan = split[0]
        out = "TOPIC {} :{}".format(chan, message)
    else:
        message = " ".join(split)
        out = "TOPIC {} :{}".format(chan, message)
    conn.send(out)


@hook.command(permissions=["op_kick", "op"])
def kick(inp, chan=None, conn=None, notice=None):
    """kick [channel] <user> [reason] -- Makes the bot kick <user> in [channel]
    If [channel] is blank the bot will kick the <user> in
    the channel the command was used in."""
    split = inp.split(" ")

    if split[0].startswith("#"):
        channel = split[0]
        target = split[1]
        if len(split) > 2:
            reason = " ".join(split[2:])
            out = "KICK {} {}: {}".format(channel, target, reason)
        else:
            out = "KICK {} {}".format(channel, target)
    else:
        channel = chan
        target = split[0]
        if len(split) > 1:
            reason = " ".join(split[1:])
            out = "KICK {} {} :{}".format(channel, target, reason)
        else:
            out = "KICK {} {}".format(channel, target)

    notice("Attempting to kick {} from {}...".format(target, channel))
    conn.send(out)


@hook.command(permissions=["op_rem", "op"])
def remove(inp, chan=None, conn=None):
    """remove [channel] [user] -- Force a user to part from a channel."""
    split = inp.split(" ")
    if split[0].startswith("#"):
        message = " ".join(split[1:])
        chan = split[0]
        out = "REMOVE {} :{}".format(chan, message)
    else:
        message = " ".join(split)
        out = "REMOVE {} :{}".format(chan, message)
    conn.send(out)


@hook.command(permissions=["op_mute", "op"], autohelp=False)
def mute(inp, conn=None, chan=None, notice=None):
    """mute [channel] -- Makes the bot mute a channel..
    If [channel] is blank the bot will mute
    the channel the command was used in."""
    mode_cmd_no_target("+m", "mute", inp, chan, conn, notice)


@hook.command(permissions=["op_mute", "op"], autohelp=False)
def unmute(inp, conn=None, chan=None, notice=None):
    """mute [channel] -- Makes the bot mute a channel..
    If [channel] is blank the bot will mute
    the channel the command was used in."""
    mode_cmd_no_target("-m", "unmute", inp, chan, conn, notice)


@hook.command(permissions=["op_lock", "op"], autohelp=False)
def lock(inp, conn=None, chan=None, notice=None):
    """lock [channel] -- Makes the bot lock a channel.
    If [channel] is blank the bot will mute
    the channel the command was used in."""
    mode_cmd_no_target("+i", "lock", inp, chan, conn, notice)


@hook.command(permissions=["op_lock", "op"], autohelp=False)
def unlock(inp, conn=None, chan=None, notice=None):
    """unlock [channel] -- Makes the bot unlock a channel..
    If [channel] is blank the bot will mute
    the channel the command was used in."""
    mode_cmd_no_target("-i", "unlock", inp, chan, conn, notice)
