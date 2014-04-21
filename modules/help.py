import re

from util import hook


@hook.command("help", autohelp=False)
def help_command(text, notice, conn, bot):
    """help  -- Gives a list of commands/help for a command."""

    funcs = {}
    disabled = bot.config.get('disabled_plugins', [])
    disabled_comm = bot.config.get('disabled_commands', [])
    for command, (func, args) in bot.commands.items():
        fn = re.match(r'^modules.(.+).py$', func._filename)
        if fn is None and (func._filename not in disabled) or (fn.group(1).lower() not in disabled):
            if command not in disabled_comm:
                if func.__doc__ is not None:
                    if func in funcs:
                        if len(funcs[func]) < len(command):
                            funcs[func] = command
                    else:
                        funcs[func] = command

    commands = dict((value, key) for key, value in funcs.items())

    if not text:
        out = [""]
        well = []
        for x in commands:
            well.append(x)
        well.sort()
        count = 0
        for x in well:
            if len(out[count]) + len(str(x)) > 405:
                count += 1
                out.append(str(x))
            else:
                out[count] += " " + str(x)

        notice("Commands I recognise: " + out[0][1:])
        if len(out) > 1:
            for x in out[1:]:
                notice(x)
        notice("For detailed help, do '{}help <example>' where <example> "
               "is the name of the command you want help for.".format(conn.config["command_prefix"]))

    else:
        if text in commands:
            notice(conn.config["command_prefix"] + commands[text].__doc__)
        else:
            notice("Command {}{} not found".format(conn.config["command_prefix"], text))
