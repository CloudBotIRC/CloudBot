from operator import attrgetter
import asyncio
import re

from cloudbot import hook
from cloudbot.util import formatting
    

@asyncio.coroutine
@hook.command("help", autohelp=False)
def help_command(text, chan, conn, bot, notice, message, has_permission):
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
        commands = []

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

            commands.append(command)

        # list of lines to send to the user
        lines = formatting.chunk_str("Here's a list of commands you can use: " + ", ". join(commands))

        for line in lines:
            if chan[:1] == "#":
                notice(line)
            else:
                #This is an user in this case.
                message(line)
        notice("For detailed help, use {}help <command>, without the brackets.".format(conn.config["command_prefix"]))
