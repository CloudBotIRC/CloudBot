#  Created by Lukeroge, improved by TheNoodle
from util import hook
from random import getrandbits


# yay for cryptic but fast code
def flip_simple(count):
    heads, tails = 0, 0
    for x in xrange(count):
        if not getrandbits(1):
            heads += 1
        else:
            tails += 1
    return heads, tails


@hook.command(autohelp=False)
def coin(inp):
    ".coin [amount] -- Flips [amount] of coins."
    # checking for valid input. if valid input [count=inp],
    # if invalid [return error], if no input [count=1]
    if inp.isdigit():
        count = int(inp)
    else:
        if inp:
            return "Invalid input."
        else:
            count = 1

    if count > 9001:
        return "Too many coins! Maximum is 9001."
    # depending on the count, we use two different methods to get the output
    if count == 1:
        flip = getrandbits(1)
        if flip == 1:
            return "You flip a coin and get heads."
        else:
            return "You flip a coin and get tails."
    else:
        flips = flip_simple(count)
        return "You flip %i coins and get " \
        "%i heads and %i tails." % (count, flips[0], flips[1])
