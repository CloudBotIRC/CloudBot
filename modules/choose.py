import re
import random

from cloudbot import hook


@hook.command
def choose(text, notice):
    """choose <choice1>, [choice2], [choice3], etc. -- Randomly picks one of the given choices.
    :type text: str
    """
    choices = re.findall(r'([^,\s]+)', text)
    if len(choices) == 1:
        notice(choose.__doc__)
        return
    return random.choice(choices)
