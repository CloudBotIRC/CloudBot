from util import hook, text


@hook.command
def munge(inp):
    "munge <text> -- Munges up <text>."
    return text.munge(inp)
