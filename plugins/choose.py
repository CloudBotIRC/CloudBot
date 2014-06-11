import re
import asyncio
import random

from cloudbot import hook


@asyncio.coroutine
@hook.command
def choose(text, notice):
    """<choice1>, [choice2], [choice3], etc. - randomly picks one of the given choices
    :type text: str
    """
    choices = re.findall(r'([^,\s]+)', text)
    if len(choices) == 1:
        notice(choose.__doc__)
        return
    return random.choice(choices)
