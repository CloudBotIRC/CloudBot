#  Created by Lukeroge, improved by TheNoodle
from util import hook
import random


# used for tails: x heads: y
def flip_simple(count):
    heads = 0
    tails = 0
    for x in range(count):
        c = random.randint(0, 1)
        if c == 0:
            heads += 1
        else:
            tails += 1
    return [heads, tails]


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

    if count > 200:
        return "Too many coins! Maximum is 200."
    # depending on the count, we use two different methods to get the output
    if count == 1:
        flip = random.randint(0, 1)
        if flip == 1:
            sidename = "heads"
        else:
            sidename = "tails"
        return "You flip a coin and get " + sidename + "."
    else:
        flips = flip_simple(count)
        return "You flip %s coins and get " \
        "%s heads and %s tails." % (str(count), str(flips[0]), str(flips[1]))
