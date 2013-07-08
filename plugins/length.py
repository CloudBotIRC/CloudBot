from util import hook


@hook.command
def length(inp):
    "length <message> -- gets the length of <message>"
    return "The length of that message is {} characters.".format(len(inp))
