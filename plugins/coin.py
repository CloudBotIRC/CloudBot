import random

from util import hook


@hook.command(autohelp=False)
def coin(inp, action=None):
    """coin [amount] -- Flips [amount] of coins."""

    if inp:
        try:
            amount = int(inp)
        except (ValueError, TypeError):
            return "Invalid input!"
    else:
        amount = 1

    if amount == 1:
        action("flips a coin and gets {}.".format(random.choice(["heads", "tails"])))
    elif amount == 0:
        action("makes a coin flipping motion with its hands.")
    else:
        heads = int(random.normalvariate(.5 * amount, (.75 * amount) ** .5))
        tails = amount - heads
        action("flips {} coins and gets {} heads and {} tails.".format(amount, heads, tails))
