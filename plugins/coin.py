#  Created by Lukeroge, improved by TheNoodle
from util import hook
from random import getrandbits


# yay for wtfcode
def flip_simple(count):
    heads, tails = 0, 0
    for x in xrange(count):
        if not getrandbits(1):
            heads += 1
        else:
            tails += 1
    return heads, tails


@hook.command(autohelp=False)
def coin(inp, me=None):
    "coin [amount] -- Flips [amount] of coins."

    if inp.isdigit():
        amount = int(inp)
    else:
        amount = 1

    if amount > 9001:
        return "Too many coins! Maximum is 9001."
    elif amount == 1:
        flip = getrandbits(1)
        if flip == 1:
            me("flips a coin and gets heads.")
        else:
            me("flips a coin and gets tails.")
    elif amount == 0:
        me("makes a coin flipping motion with its hands.")
    else:
        flips = flip_simple(amount)
        me("flips %i coins and gets " \
        "%i heads and %i tails." % (amount, flips[0], flips[1]))
