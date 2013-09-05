import random

from util import hook


@hook.command
def choose(inp):
    """choose <choice1>, [choice2], [choice3]
    Randomly picks one of the given choices."""

    c = inp.split(" ")
    if len(c) == 1:
        return 'banana'
    return random.choice(c).strip()
