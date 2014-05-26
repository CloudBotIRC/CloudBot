from cloudbot import hook


def mode_cmd(mode, text, text_inp, chan, conn, notice):
    """ generic mode setting function """
    split = text_inp.split(" ")
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


def mode_cmd_no_target(mode, text, text_inp, chan, conn, notice):
    """ generic mode setting function without a target"""
    split = text_inp.split(" ")
    if split[0].startswith("#"):
        channel = split[0]
        notice("Attempting to {} {}...".format(text, channel))
        conn.send("MODE {} {}".format(channel, mode))
    else:
        channel = chan
        notice("Attempting to {} {}...".format(text, channel))
        conn.send("MODE {} {}".format(channel, mode))


@hook.command(permissions=["op_ban", "op"])
def ban(text, conn, chan, notice):
    """ban [channel] <user> -- Makes the bot ban <user> in [channel].
    If [channel] is blank the bot will ban <user> in
    the channel the command was used in."""
    mode_cmd("+b", "ban", text, chan, conn, notice)


@hook.command(permissions=["op_ban", "op"])
def unban(text, conn, chan, notice):
    """unban [channel] <user> -- Makes the bot unban <user> in [channel].
    If [channel] is blank the bot will unban <user> in
    the channel the command was used in."""
    mode_cmd("-b", "unban", text, chan, conn, notice)


@hook.command(permissions=["op_quiet", "op"])
def quiet(text, conn, chan, notice):
    """quiet [channel] <user> -- Makes the bot quiet <user> in [channel].
    If [channel] is blank the bot will quiet <user> in
    the channel the command was used in."""
    mode_cmd("+q", "quiet", text, chan, conn, notice)


@hook.command(permissions=["op_quiet", "op"])
def unquiet(text, conn, chan, notice):
    """unquiet [channel] <user> -- Makes the bot unquiet <user> in [channel].
    If [channel] is blank the bot will unquiet <user> in
    the channel the command was used in."""
    mode_cmd("-q", "unquiet", text, chan, conn, notice)


@hook.command(permissions=["op_voice", "op"])
def voice(text, conn, chan, notice):
    """voice [channel] <user> -- Makes the bot voice <user> in [channel].
    If [channel] is blank the bot will voice <user> in
    the channel the command was used in."""
    mode_cmd("+v", "voice", text, chan, conn, notice)


@hook.command(permissions=["op_voice", "op"])
def devoice(text, conn, chan, notice):
    """devoice [channel] <user> -- Makes the bot devoice <user> in [channel].
    If [channel] is blank the bot will devoice <user> in
    the channel the command was used in."""
    mode_cmd("-v", "devoice", text, chan, conn, notice)


@hook.command(permissions=["op_op", "op"])
def op(text, conn, chan, notice):
    """op [channel] <user> -- Makes the bot op <user> in [channel].
    If [channel] is blank the bot will op <user> in
    the channel the command was used in."""
    mode_cmd("+o", "op", text, chan, conn, notice)


@hook.command(permissions=["op_op", "op"])
def deop(text, conn, chan, notice):
    """deop [channel] <user> -- Makes the bot deop <user> in [channel].
    If [channel] is blank the bot will deop <user> in
    the channel the command was used in."""
    mode_cmd("-o", "deop", text, chan, conn, notice)


@hook.command(permissions=["op_topic", "op"])
def topic(text, conn, chan):
    """topic [channel] <topic> -- Change the topic of a channel."""
    split = text.split(" ")
    if split[0].startswith("#"):
        message = " ".join(split[1:])
        chan = split[0]
    else:
        message = " ".join(split)
    conn.send("TOPIC {} :{}".format(chan, message))


@hook.command(permissions=["op_kick", "op"])
def kick(text, chan, conn, notice):
    """kick [channel] <user> [reason] -- Makes the bot kick <user> in [channel]
    If [channel] is blank the bot will kick the <user> in
    the channel the command was used in."""
    split = text.split(" ")

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
def remove(text, chan, conn):
    """remove [channel] [user] -- Force a user to part from a channel."""
    split = text.split(" ")
    if split[0].startswith("#"):
        message = " ".join(split[1:])
        chan = split[0]
        out = "REMOVE {} :{}".format(chan, message)
    else:
        message = " ".join(split)
        out = "REMOVE {} :{}".format(chan, message)
    conn.send(out)


@hook.command(permissions=["op_mute", "op"], autohelp=False)
def mute(text, conn, chan, notice):
    """mute [channel] -- Makes the bot mute a channel..
    If [channel] is blank the bot will mute
    the channel the command was used in."""
    mode_cmd_no_target("+m", "mute", text, chan, conn, notice)


@hook.command(permissions=["op_mute", "op"], autohelp=False)
def unmute(text, conn, chan, notice):
    """mute [channel] -- Makes the bot mute a channel..
    If [channel] is blank the bot will mute
    the channel the command was used in."""
    mode_cmd_no_target("-m", "unmute", text, chan, conn, notice)


@hook.command(permissions=["op_lock", "op"], autohelp=False)
def lock(text, conn, chan, notice):
    """lock [channel] -- Makes the bot lock a channel.
    If [channel] is blank the bot will mute
    the channel the command was used in."""
    mode_cmd_no_target("+i", "lock", text, chan, conn, notice)


@hook.command(permissions=["op_lock", "op"], autohelp=False)
def unlock(text, conn, chan, notice):
    """unlock [channel] -- Makes the bot unlock a channel..
    If [channel] is blank the bot will mute
    the channel the command was used in."""
    mode_cmd_no_target("-i", "unlock", text, chan, conn, notice)
