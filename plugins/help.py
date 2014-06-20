from operator import attrgetter
import asyncio
import re

from cloudbot import hook


@asyncio.coroutine
@hook.command("help", autohelp=False)
def help_command(text, conn, bot, notice, has_permission):
    """[command] - gives help for [command], or lists all available commands if no command is specified
    :type text: str
    :type conn: cloudbot.client.Client
    :type bot: cloudbot.bot.CloudBot
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
                if doc.split()[0].isalpha():
                    # this is using the old format of `name <args> - doc`
                    message = "{}{}".format(conn.config["command_prefix"], doc)
                else:
                    # this is using the new format of `<args> - doc`
                    message = "{}{} {}".format(conn.config["command_prefix"], searching_for, doc)
                notice(message)
            else:
                notice("Command {} has no additional documentation.".format(searching_for))
        else:
            notice("Unknown command '{}'".format(searching_for))
    else:

        # list of lines to send to the user
        lines = []
        # current line, containing words to join with " "
        current_line = []
        # current line length, to count how long the current line will be when joined with " "
        current_line_length = 0

        for plugin in sorted(set(bot.plugin_manager.commands.values()), key=attrgetter("name")):
            # use set to remove duplicate commands (from multiple aliases), and sorted to sort by name

            if plugin.permissions:
                # check permissions
                allowed = False
                for perm in plugin.permissions:
                    if has_permission(perm, notice=False):
                        allowed = True
                        break

                if not allowed:
                    # skip adding this command
                    continue

            # add the command to lines sent
            command = plugin.name
            added_length = len(command) + 2  # + 2 to account for space and comma

            if current_line_length + added_length > 450:
                # if line limit is reached, add line to lines, and reset
                lines.append(", ".join(current_line) + ",")
                current_line = []
                current_line_length = 0

            current_line.append(command)
            current_line_length += added_length

        if current_line:
            # make sure to include the last line
            lines.append(", ".join(current_line))

        notice("Here's a list of commands you can use:")
        for line in lines:
            notice(line)
        notice("For detailed help, use {}help <command>, without the brackets.".format(conn.config["command_prefix"]))
