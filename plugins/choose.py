import re
import random

from util import hook


@hook.command
def choose(inp, notice=None):
    """choose <choice1>, [choice2], [choice3], etc. -- Randomly picks one of the given choices.
    :type inp: str
    """
    choices = re.findall(r'([^,\s]+)', inp)
    if len(choices) == 1:
        notice(choose.__doc__)
        return
    return random.choice(choices)
