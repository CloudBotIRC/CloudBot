import random

from util import hook


@hook.command(autohelp=False)
def coin(inp, notice=None, action=None):
    """coin [amount] -- Flips [amount] of coins.
    :type inp: str
    """

    if inp:
        try:
            amount = int(inp)
        except (ValueError, TypeError):
            notice("Invalid input '{}': not a number".format(inp))
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
