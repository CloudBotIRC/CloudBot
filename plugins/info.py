from util import hook


@hook.command(autohelp=False)
def channels(inp, conn=None):
    "channels -- Lists the channels that the bot is in."
    return "I am in these channels: %s" % ", ".join(conn.channels)


@hook.command(autohelp=False)
def prefix(inp, notice=False, conn=False):
    "prefix -- Shows the bot's command prefix"
    notice('The command prefix is "%s"' % conn.conf["command_prefix"])
