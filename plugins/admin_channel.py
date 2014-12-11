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
    """[channel] <user> - bans <user> in [channel], or in the caller's channel if no channel is specified"""
    mode_cmd("+b", "ban", text, chan, conn, notice)


@hook.command(permissions=["op_ban", "op"])
def unban(text, conn, chan, notice):
    """[channel] <user> - unbans <user> in [channel], or in the caller's channel if no channel is specified"""
    mode_cmd("-b", "unban", text, chan, conn, notice)


@hook.command(permissions=["op_quiet", "op"])
def quiet(text, conn, chan, notice):
    """[channel] <user> - quiets <user> in [channel], or in the caller's channel if no channel is specified"""
    mode_cmd("+q", "quiet", text, chan, conn, notice)


@hook.command(permissions=["op_quiet", "op"])
def unquiet(text, conn, chan, notice):
    """[channel] <user> - unquiets <user> in [channel], or in the caller's channel if no channel is specified"""
    mode_cmd("-q", "unquiet", text, chan, conn, notice)


@hook.command(permissions=["op_voice", "op"])
def voice(text, conn, chan, notice):
    """[channel] <user> - voices <user> in [channel], or in the caller's channel if no channel is specified"""
    mode_cmd("+v", "voice", text, chan, conn, notice)


@hook.command(permissions=["op_voice", "op"])
def devoice(text, conn, chan, notice):
    """[channel] <user> - devoices <user> in [channel], or in the caller's channel if no channel is specified"""
    mode_cmd("-v", "devoice", text, chan, conn, notice)


@hook.command(permissions=["op_op", "op"])
def op(text, conn, chan, notice):
    """[channel] <user> - ops <user> in [channel], or in the caller's channel if no channel is specified"""
    mode_cmd("+o", "op", text, chan, conn, notice)


@hook.command(permissions=["op_op", "op"])
def deop(text, conn, chan, notice):
    """[channel] <user> - deops <user> in [channel], or in the caller's channel if no channel is specified"""
    mode_cmd("-o", "deop", text, chan, conn, notice)


@hook.command(permissions=["op_topic", "op"])
def topic(text, conn, chan):
    """[channel] <topic> - changes the topic to <topic> in [channel], or in the caller's channel
     if no channel is specified"""
    split = text.split(" ")
    if split[0].startswith("#"):
        message = " ".join(split[1:])
        chan = split[0]
    else:
        message = " ".join(split)
    conn.send("TOPIC {} :{}".format(chan, message))


@hook.command(permissions=["op_kick", "op"])
def kick(text, chan, conn, notice):
    """[channel] <user> - kicks <user> from [channel], or from the caller's channel if no channel is specified"""
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
    """[channel] <user> - force removes <user> from [channel], or in the caller's channel if no channel is specified"""
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
    """[channel] - mutes [channel], or in the caller's channel if no channel is specified"""
    mode_cmd_no_target("+m", "mute", text, chan, conn, notice)


@hook.command(permissions=["op_mute", "op"], autohelp=False)
def unmute(text, conn, chan, notice):
    """[channel] - unmutes [channel], or in the caller's channel if no channel is specified"""
    mode_cmd_no_target("-m", "unmute", text, chan, conn, notice)


@hook.command(permissions=["op_lock", "op"], autohelp=False)
def lock(text, conn, chan, notice):
    """[channel] - locks [channel], or in the caller's channel if no channel is specified"""
    mode_cmd_no_target("+i", "lock", text, chan, conn, notice)


@hook.command(permissions=["op_lock", "op"], autohelp=False)
def unlock(text, conn, chan, notice):
    """[channel] - unlocks [channel], or in the caller's channel if no channel is specified"""
    mode_cmd_no_target("-i", "unlock", text, chan, conn, notice)
