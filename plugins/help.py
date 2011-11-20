import re

from util import hook

# Standard automatic help command
@hook.command(autohelp=False)
def help(inp, input=None, bot=None, say=None, notice=None):
    ".help  -- gives a list of commands/help for a command"

    funcs = {}
    disabled = bot.config.get('disabled_plugins', [])
    disabled_comm = bot.config.get('disabled_commands', [])
    for command, (func, args) in bot.commands.iteritems():
        fn = re.match(r'^plugins.(.+).py$', func._filename)
        if fn.group(1).lower() not in disabled:
            if command not in disabled_comm:
                if func.__doc__ is not None:
                    if func in funcs:
                        if len(funcs[func]) < len(command):
                            funcs[func] = command
                    else:
                        funcs[func] = command

    hidden = ["part", "stfu", "kthx", "chnick", "join", "8ballnooxt"]

    commands = dict((value, key) for key, value in funcs.iteritems() if key not in hidden)

    if not inp:
        length = 0
        out = ["",""]
        well = []
        for x in commands:
            if x not in hidden:
                well.append(x)
        well.sort()
        for x in well:
            if len(out[0]) + len(str(x)) > 440:
                out[1] += " " + str(x)
            else:
                out[0] += " " + str(x)
        
        notice(out[0][1:])
        if out[1]:
            notice(out[1][1:])
        
        
        
    else:
        if inp in commands:
            input.say(commands[inp].__doc__)

