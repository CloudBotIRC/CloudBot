import asyncio
import random
import re

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


@asyncio.coroutine
@hook.command(autohelp=False)
def coin(text, notice, action):
    """[amount] - flips [amount] coins
    :type text: str
    """

    if text:
        try:
            amount = int(text)
        except (ValueError, TypeError):
            notice("Invalid input '{}': not a number".format(text))
            return
    else:
        amount = 1

    if amount == 1:
        action("flips a coin and gets {}.".format(random.choice(["heads", "tails"])))
    elif amount == 0:
        action("makes a coin flipping motion")
    else:
        heads = int(random.normalvariate(.5 * amount, (.75 * amount) ** .5))
        tails = amount - heads
        action("flips {} coins and gets {} heads and {} tails.".format(amount, heads, tails))
