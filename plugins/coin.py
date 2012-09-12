from util import hook
import random


@hook.command(autohelp=False)
def coin(inp, me=None):
    "coin [amount] -- Flips [amount] of coins."

    if inp:
        try:
            amount = int(inp)
        except (ValueError, TypeError):
            return "Invalid input!"
    else:
        amount = 1

    if amount == 1:
        me("flips a coin and gets %s." % random.choice(["heads", "tails"]))
    elif amount == 0:
        me("makes a coin flipping motion with its hands.")
    else:
        heads = int(random.normalvariate(.5 * amount, (.75 * amount) ** .5))
        tails = amount - heads
        me("flips %i coins and gets " \
        "%i heads and %i tails." % (amount, heads, tails))
