from util import hook
from random import getrandbits, normalvariate


@hook.command(autohelp=False)
def coin(inp, me=None):
    "coin [amount] -- Flips [amount] of coins."

    if inp.isdigit():
        amount = int(inp)
    else:
        amount = 1

    if amount > 90001:
        return "Too many coins! Maximum is 90001."
    elif amount == 1:
        if getrandbits(1):
            me("flips a coin and gets heads.")
        else:
            me("flips a coin and gets tails.")
    elif amount == 0:
        me("makes a coin flipping motion with its hands.")
    else:
        heads = int(normalvariate(.5 * amount, (.75 * amount) ** .5))
        tails = amount - heads
        me("flips %i coins and gets " \
        "%i heads and %i tails." % (amount, heads, tails))
