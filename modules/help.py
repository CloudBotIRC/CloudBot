import re

from util import hook


@hook.command("help", autohelp=False)
def help_command(text, conn, bot, notice, has_permission):
    """help  -- Gives a list of commands/help for a command.
    :type text: str
    :type conn: core.irc.BotConnection
    :type bot: core.bot.CloudBot
    """
    if text:
        searching_for = text.lower().strip()
        if not re.match(r'^\w+$', searching_for):
            notice("Invalid command name '{}'".format(text))
            return
    else:
        searching_for = None

    if searching_for:
        if searching_for in bot.plugin_manager.commands:
            doc = bot.plugin_manager.commands[searching_for].doc
            if doc:
                notice(conn.config["command_prefix"] + doc)
            else:
                notice("Command {} has no additional documentation.".format(searching_for))
        else:
            notice("Unknown command '{}'".format(searching_for))
    else:
        available_commands = []
        for command_plugin in bot.plugin_manager.commands.values():
            if not command_plugin.args.get("permissions"):
                available_commands.append(command_plugin.name)
            else:
                for perm in command_plugin.args.get("permissions"):
                    if has_permission(perm, notice=False):
                        available_commands.append(command_plugin.name)
                        break
        print(available_commands)
        lines = []
        current_line = []
        current_line_length = 0
        for command in available_commands:
            if current_line_length + len(command) > 405:  # line limit
                lines.append(", ".join(current_line))
                current_line = []
                current_line_length = 0

            current_line.append(command)
            current_line_length += len(command) + 2  # + 2 to account for space and comma

        if current_line:
            lines.append(", ".join(current_line))  # make sure to include the last line

        notice("Commands use can use:")
        for line in lines:
            notice(line)
        notice("For detailed help, use {}help <commands>, without the brackets.".format(conn.config["command_prefix"]))
