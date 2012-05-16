from util import hook

@hook.command(autohelp=False)
def admins(inp, notice=None, bot=None):
    "admins -- Lists bot's admins."
    if bot.config["admins"]:
        notice("Admins are: %s." % ", ".join(bot.config["admins"]))
    else:
        notice("No users are admins!")
    return


@hook.command(autohelp=False)
def prefix(inp, notice=False, conn=False):
    "prefix -- Shows the bot's command prefix"
    notice("The prefix is: \"%s\"" % conn.conf["command_prefix"])